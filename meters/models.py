from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    accessible_views = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.user.username

class Block(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='companies'
    )
    block = models.ForeignKey(
        Block, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='companies'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class MeterConfig(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='meter_configs')
    service_no = models.CharField(max_length=100)
    tariff = models.CharField(max_length=100)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    kw_kva = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    ctr_enabled = models.BooleanField(default=False)
    ctr_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    genset = models.ForeignKey('Genset', on_delete=models.SET_NULL, null=True, blank=True, related_name='meter_configs')
    fixed_demand = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.name} - {self.service_no} ({self.effective_date})"


class MeterReading(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='readings'
    )
    reading_date = models.DateField()
    previous_reading = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    current_reading = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    reading_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)  # units consumed
    peak_hour_enabled = models.BooleanField(default=False)
    peak_hour_manual_override = models.BooleanField(default=False)
    peak_hour_manual_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.name} - {self.reading_date} - {self.reading_value} units"


class GensetReading(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='genset_readings')
    reading_date = models.DateField()
    previous_reading = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    current_reading = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    reading_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)  # units consumed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Genset: {self.company.name} - {self.reading_date} - {self.reading_value} units"


class Genset(models.Model):
    name = models.CharField(max_length=255)
    kva_capacity_text = models.CharField(max_length=255, help_text="e.g. 250 + 250")
    total_kva = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


    @property
    def current_stock(self):
        latest_entry = self.diesel_entries.order_by('-entry_date', '-id').first()
        if latest_entry:
            return latest_entry.closing_stock
        return 0

class TaxRate(models.Model):
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Tax percentage (e.g., 5.00 for 5%)")
    effective_date = models.DateField(help_text="Date from which this tax rate is effective")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.percentage}% (Effective: {self.effective_date})"

    class Meta:
        ordering = ['-effective_date']

class DieselRate(models.Model):
    price_per_liter = models.DecimalField(max_digits=10, decimal_places=2, help_text="Diesel price per liter (e.g., 90.50)")
    effective_date = models.DateField(help_text="Date from which this price is effective")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"₹{self.price_per_liter}/L (Effective: {self.effective_date})"

    class Meta:
        ordering = ['-effective_date']

class DieselEntry(models.Model):
    genset = models.ForeignKey(Genset, on_delete=models.CASCADE, related_name='diesel_entries')
    entry_date = models.DateField(default=timezone.now)
    opening_stock = models.DecimalField(max_digits=10, decimal_places=2, help_text="Stock before entry")
    purchased_liters = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Diesel purchased")
    consumed_liters = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Diesel consumed")
    closing_stock = models.DecimalField(max_digits=10, decimal_places=2, help_text="Stock after entry")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-entry_date', '-id']

    def __str__(self):
        return f"{self.genset.name} - {self.entry_date} (P: {self.purchased_liters}L, C: {self.consumed_liters}L)"

class FacilityBillingUnit(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='billing_units')
    unit_count = models.IntegerField(help_text="Number of units (e.g. 500 people, 12 shops)")
    unit_type = models.CharField(max_length=50, help_text="Type of generic unit (e.g. 'People', 'Shops')")
    effective_date = models.DateField(help_text="Date from which this billing unit is effective")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-effective_date']
        unique_together = ('category', 'effective_date')

    def __str__(self):
        return f"{self.category.name} - {self.unit_count} {self.unit_type} (Effective: {self.effective_date})"

class PowerCut(models.Model):
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"Power Cut: {self.date} ({self.start_time} - {self.end_time})"

class PowerHouseComplaint(models.Model):
    date = models.DateField(default=timezone.now)
    is_block_location = models.BooleanField(default=True)
    block = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    manual_location = models.CharField(max_length=255, null=True, blank=True)
    complaint_request = models.CharField(max_length=300)
    start_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    end_time = models.TimeField(null=True, blank=True)
    duration = models.CharField(max_length=10, null=True, blank=True, help_text="HH:MM format")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        loc = self.block.name if self.is_block_location and self.block else self.manual_location
        return f"Complaint at {loc} on {self.date}"
