import math
from rest_framework import serializers
from .models import (
    Block, Category, Company, MeterConfig, MeterReading, Genset,
    TaxRate, DieselRate, GensetReading, DieselEntry, FacilityBillingUnit, PowerCut,
    PowerHouseComplaint
)


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class GensetSerializer(serializers.ModelSerializer):
    current_stock = serializers.ReadOnlyField()

    class Meta:
        model = Genset
        fields = '__all__'


class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = '__all__'


class DieselRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DieselRate
        fields = '__all__'


class MeterConfigSerializer(serializers.ModelSerializer):
    genset_name = serializers.ReadOnlyField(source='genset.name')

    class Meta:
        model = MeterConfig
        fields = [
            'id', 'company', 'service_no', 'tariff', 'unit_cost', 'kw_kva',
            'fixed_demand', 'effective_date', 'ctr_enabled', 'ctr_value',
            'genset', 'genset_name', 'created_at'
        ]


class CompanySerializer(serializers.ModelSerializer):
    meter_configs = MeterConfigSerializer(many=True, read_only=True)
    category_name = serializers.ReadOnlyField(source='category.name')
    block_name = serializers.ReadOnlyField(source='block.name')

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'category', 'category_name',
            'block', 'block_name', 'created_at', 'meter_configs'
        ]


class MeterReadingSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    category_name = serializers.ReadOnlyField(source='company.category.name')
    block_name = serializers.ReadOnlyField(source='company.block.name')
    unit_rate = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    fixed_demand = serializers.SerializerMethodField()
    per_kva = serializers.SerializerMethodField()
    fd_price = serializers.SerializerMethodField()
    peak_hour_charges = serializers.SerializerMethodField()
    stotal = serializers.SerializerMethodField()
    tax_percentage = serializers.SerializerMethodField()
    tax_amount = serializers.SerializerMethodField()
    net_amount = serializers.SerializerMethodField()

    class Meta:
        model = MeterReading
        fields = [
            'id', 'company', 'company_name', 'category_name', 'block_name',
            'reading_date', 'previous_reading', 'current_reading',
            'reading_value', 'peak_hour_enabled',
            'peak_hour_manual_override', 'peak_hour_manual_value',
            'unit_rate', 'amount',
            'fixed_demand', 'per_kva', 'fd_price',
            'peak_hour_charges', 'stotal', 'tax_percentage', 'tax_amount',
            'net_amount', 'created_at'
        ]

    def _get_config(self, obj):
        return (
            MeterConfig.objects
            .filter(company=obj.company, effective_date__lte=obj.reading_date)
            .order_by('-effective_date')
            .first()
        )

    def _get_rate_and_units(self, obj, config):
        if config is None:
            return None, None
        units = float(obj.reading_value)
        rate = float(config.unit_cost)
        return units, rate

    def get_unit_rate(self, obj):
        config = self._get_config(obj)
        return float(config.unit_cost) if config else None

    def get_amount(self, obj):
        config = self._get_config(obj)
        if config is None:
            return None
        units, rate = self._get_rate_and_units(obj, config)
        return round(units * rate, 2)

    def get_fixed_demand(self, obj):
        config = self._get_config(obj)
        if config and config.fixed_demand is not None:
            return float(config.fixed_demand)
        return None

    def get_per_kva(self, obj):
        config = self._get_config(obj)
        return float(config.kw_kva) if config else None

    def get_fd_price(self, obj):
        config = self._get_config(obj)
        if config and config.fixed_demand is not None:
            return round(float(config.fixed_demand) * float(config.kw_kva), 2)
        return None

    def get_peak_hour_charges(self, obj):
        if not obj.peak_hour_enabled:
            return 0.0
        # Manual override: use the user-entered value directly
        if (obj.peak_hour_manual_override and
                obj.peak_hour_manual_value is not None):
            return float(obj.peak_hour_manual_value)
        # Auto-calculate: (units * 25%) * (rate * 20%)
        config = self._get_config(obj)
        if config is None:
            return 0.0
        units, rate = self._get_rate_and_units(obj, config)
        return round((units * 0.25) * (rate * 0.20), 2)

    def get_stotal(self, obj):
        amount = self.get_amount(obj)
        fd_price = self.get_fd_price(obj)
        peak = self.get_peak_hour_charges(obj)
        if amount is None:
            return None
        base = amount + (fd_price or 0)
        if obj.peak_hour_enabled:
            base += (peak or 0)
        return round(base, 2)

    def _get_tax_rate(self, obj):
        return (
            TaxRate.objects
            .filter(effective_date__lte=obj.reading_date)
            .order_by('-effective_date')
            .first()
        )

    def get_tax_percentage(self, obj):
        tax = self._get_tax_rate(obj)
        if tax:
            return float(tax.percentage)
        return 5.0  # fallback to 5% if no configuration is found

    def get_tax_amount(self, obj):
        stotal = self.get_stotal(obj)
        if stotal is None:
            return None
        percentage = self.get_tax_percentage(obj)
        return round(stotal * (percentage / 100), 2)

    def get_net_amount(self, obj):
        stotal = self.get_stotal(obj)
        tax = self.get_tax_amount(obj)
        if stotal is None or tax is None:
            return None
        return math.ceil(stotal + tax)


class GensetReadingSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    category_name = serializers.ReadOnlyField(source='company.category.name')
    block_name = serializers.ReadOnlyField(source='company.block.name')

    class Meta:
        model = GensetReading
        fields = [
            'id', 'company', 'company_name', 'category_name', 'block_name',
            'reading_date', 'previous_reading', 'current_reading',
            'reading_value', 'created_at'
        ]


class DieselEntrySerializer(serializers.ModelSerializer):
    genset_name = serializers.CharField(source='genset.name', read_only=True)

    class Meta:
        model = DieselEntry
        fields = '__all__'


class FacilityBillingUnitSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

class GensetSerializer(serializers.ModelSerializer):
    current_stock = serializers.ReadOnlyField()

    class Meta:
        model = Genset
        fields = '__all__'


class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = '__all__'


class DieselRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DieselRate
        fields = '__all__'


class MeterConfigSerializer(serializers.ModelSerializer):
    genset_name = serializers.ReadOnlyField(source='genset.name')

    class Meta:
        model = MeterConfig
        fields = [
            'id', 'company', 'service_no', 'tariff', 'unit_cost', 'kw_kva',
            'fixed_demand', 'effective_date', 'ctr_enabled', 'ctr_value',
            'genset', 'genset_name', 'created_at'
        ]


class CompanySerializer(serializers.ModelSerializer):
    meter_configs = MeterConfigSerializer(many=True, read_only=True)
    category_name = serializers.ReadOnlyField(source='category.name')
    block_name = serializers.ReadOnlyField(source='block.name')

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'category', 'category_name',
            'block', 'block_name', 'created_at', 'meter_configs'
        ]


class MeterReadingSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    category_name = serializers.ReadOnlyField(source='company.category.name')
    block_name = serializers.ReadOnlyField(source='company.block.name')
    unit_rate = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    fixed_demand = serializers.SerializerMethodField()
    per_kva = serializers.SerializerMethodField()
    fd_price = serializers.SerializerMethodField()
    peak_hour_charges = serializers.SerializerMethodField()
    stotal = serializers.SerializerMethodField()
    tax_percentage = serializers.SerializerMethodField()
    tax_amount = serializers.SerializerMethodField()
    net_amount = serializers.SerializerMethodField()

    class Meta:
        model = MeterReading
        fields = [
            'id', 'company', 'company_name', 'category_name', 'block_name',
            'reading_date', 'previous_reading', 'current_reading',
            'reading_value', 'peak_hour_enabled',
            'peak_hour_manual_override', 'peak_hour_manual_value',
            'unit_rate', 'amount',
            'fixed_demand', 'per_kva', 'fd_price',
            'peak_hour_charges', 'stotal', 'tax_percentage', 'tax_amount',
            'net_amount', 'created_at'
        ]

    def _get_config(self, obj):
        return (
            MeterConfig.objects
            .filter(company=obj.company, effective_date__lte=obj.reading_date)
            .order_by('-effective_date')
            .first()
        )

    def _get_rate_and_units(self, obj, config):
        if config is None:
            return None, None
        units = float(obj.reading_value)
        rate = float(config.unit_cost)
        return units, rate

    def get_unit_rate(self, obj):
        config = self._get_config(obj)
        return float(config.unit_cost) if config else None

    def get_amount(self, obj):
        config = self._get_config(obj)
        if config is None:
            return None
        units, rate = self._get_rate_and_units(obj, config)
        return round(units * rate, 2)

    def get_fixed_demand(self, obj):
        config = self._get_config(obj)
        if config and config.fixed_demand is not None:
            return float(config.fixed_demand)
        return None

    def get_per_kva(self, obj):
        config = self._get_config(obj)
        return float(config.kw_kva) if config else None

    def get_fd_price(self, obj):
        config = self._get_config(obj)
        if config and config.fixed_demand is not None:
            return round(float(config.fixed_demand) * float(config.kw_kva), 2)
        return None

    def get_peak_hour_charges(self, obj):
        if not obj.peak_hour_enabled:
            return 0.0
        # Manual override: use the user-entered value directly
        if (obj.peak_hour_manual_override and
                obj.peak_hour_manual_value is not None):
            return float(obj.peak_hour_manual_value)
        # Auto-calculate: (units * 25%) * (rate * 20%)
        config = self._get_config(obj)
        if config is None:
            return 0.0
        units, rate = self._get_rate_and_units(obj, config)
        return round((units * 0.25) * (rate * 0.20), 2)

    def get_stotal(self, obj):
        amount = self.get_amount(obj)
        fd_price = self.get_fd_price(obj)
        peak = self.get_peak_hour_charges(obj)
        if amount is None:
            return None
        base = amount + (fd_price or 0)
        if obj.peak_hour_enabled:
            base += (peak or 0)
        return round(base, 2)

    def _get_tax_rate(self, obj):
        return (
            TaxRate.objects
            .filter(effective_date__lte=obj.reading_date)
            .order_by('-effective_date')
            .first()
        )

    def get_tax_percentage(self, obj):
        tax = self._get_tax_rate(obj)
        if tax:
            return float(tax.percentage)
        return 5.0  # fallback to 5% if no configuration is found

    def get_tax_amount(self, obj):
        stotal = self.get_stotal(obj)
        if stotal is None:
            return None
        percentage = self.get_tax_percentage(obj)
        return round(stotal * (percentage / 100), 2)

    def get_net_amount(self, obj):
        stotal = self.get_stotal(obj)
        tax = self.get_tax_amount(obj)
        if stotal is None or tax is None:
            return None
        return math.ceil(stotal + tax)


class GensetReadingSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    category_name = serializers.ReadOnlyField(source='company.category.name')
    block_name = serializers.ReadOnlyField(source='company.block.name')

    class Meta:
        model = GensetReading
        fields = [
            'id', 'company', 'company_name', 'category_name', 'block_name',
            'reading_date', 'previous_reading', 'current_reading',
            'reading_value', 'created_at'
        ]


class DieselEntrySerializer(serializers.ModelSerializer):
    genset_name = serializers.CharField(source='genset.name', read_only=True)

    class Meta:
        model = DieselEntry
        fields = '__all__'


class FacilityBillingUnitSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = FacilityBillingUnit
        fields = '__all__'


class PowerCutSerializer(serializers.ModelSerializer):
    class Meta:
        model = PowerCut
        fields = '__all__'


class PowerHouseComplaintSerializer(serializers.ModelSerializer):
    block_name = serializers.ReadOnlyField(source='block.name')

    class Meta:
        model = PowerHouseComplaint
        fields = '__all__'


from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    accessible_views = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        write_only=False,
        required=False
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'is_superuser', 'date_joined', 'accessible_views']
        read_only_fields = ['is_superuser', 'date_joined']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        try:
            ret['accessible_views'] = instance.profile.accessible_views or {}
        except Exception:
            ret['accessible_views'] = {}
        return ret

    def create(self, validated_data):
        accessible_views = validated_data.pop('accessible_views', {})
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, accessible_views=accessible_views)
        return user

    def update(self, instance, validated_data):
        accessible_views = validated_data.pop('accessible_views', None)
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if accessible_views is not None:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            profile.accessible_views = accessible_views
            profile.save()
            
        return instance
