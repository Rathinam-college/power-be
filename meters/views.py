from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Block, Category, Company, MeterConfig, MeterReading, Genset,
    TaxRate, DieselRate, GensetReading, DieselEntry, FacilityBillingUnit,
    PowerCut, PowerHouseComplaint
)
from .serializers import (
    BlockSerializer, CategorySerializer, CompanySerializer,
    MeterConfigSerializer, MeterReadingSerializer, GensetSerializer,
    TaxRateSerializer, DieselRateSerializer, GensetReadingSerializer,
    DieselEntrySerializer, FacilityBillingUnitSerializer, PowerCutSerializer,
    PowerHouseComplaintSerializer, UserSerializer
)
from django.contrib.auth.models import User

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response({"detail": "Authentication credentials were not provided."}, status=401)


class BlockViewSet(viewsets.ModelViewSet):
    queryset = Block.objects.all().order_by('name')
    serializer_class = BlockSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class MeterConfigViewSet(viewsets.ModelViewSet):
    queryset = MeterConfig.objects.all()
    serializer_class = MeterConfigSerializer


class MeterReadingViewSet(viewsets.ModelViewSet):
    queryset = MeterReading.objects.all().order_by('reading_date', 'id')
    serializer_class = MeterReadingSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        company_id = self.request.query_params.get('company')
        if company_id:
            qs = qs.filter(company_id=company_id)
        return qs


class GensetReadingViewSet(viewsets.ModelViewSet):
    queryset = GensetReading.objects.all().order_by('reading_date', 'id')
    serializer_class = GensetReadingSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        company_id = self.request.query_params.get('company')
        if company_id:
            qs = qs.filter(company_id=company_id)
        return qs


class GensetViewSet(viewsets.ModelViewSet):
    queryset = Genset.objects.all().order_by('name')
    serializer_class = GensetSerializer


class TaxRateViewSet(viewsets.ModelViewSet):
    queryset = TaxRate.objects.all()
    serializer_class = TaxRateSerializer


class DieselRateViewSet(viewsets.ModelViewSet):
    queryset = DieselRate.objects.all().order_by('-effective_date')
    serializer_class = DieselRateSerializer


class DieselEntryViewSet(viewsets.ModelViewSet):
    queryset = DieselEntry.objects.all()
    serializer_class = DieselEntrySerializer

    def get_queryset(self):
        queryset = DieselEntry.objects.all().order_by('-entry_date', '-id')
        genset_id = self.request.query_params.get('genset', None)
        if genset_id is not None:
            queryset = queryset.filter(genset_id=genset_id)
        return queryset


class FacilityBillingUnitViewSet(viewsets.ModelViewSet):
    queryset = FacilityBillingUnit.objects.all()
    serializer_class = FacilityBillingUnitSerializer


class PowerCutViewSet(viewsets.ModelViewSet):
    queryset = PowerCut.objects.all().order_by('-date', '-start_time')
    serializer_class = PowerCutSerializer


class PowerHouseComplaintViewSet(viewsets.ModelViewSet):
    queryset = PowerHouseComplaint.objects.all().order_by('-date', '-start_time')
    serializer_class = PowerHouseComplaintSerializer
