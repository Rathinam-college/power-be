from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlockViewSet, CategoryViewSet, CompanyViewSet,
    MeterConfigViewSet, MeterReadingViewSet, GensetViewSet, TaxRateViewSet,
    DieselRateViewSet, DieselEntryViewSet, FacilityBillingUnitViewSet,
    PowerCutViewSet, PowerHouseComplaintViewSet, GensetReadingViewSet,
    UserViewSet
)

router = DefaultRouter()
router.register(r'blocks', BlockViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'configs', MeterConfigViewSet)
router.register(r'readings', MeterReadingViewSet)
router.register(r'gensets', GensetViewSet)
router.register(r'taxes', TaxRateViewSet)
router.register(r'diesel-prices', DieselRateViewSet)
router.register(r'genset-readings', GensetReadingViewSet)
router.register(r'diesel-entries', DieselEntryViewSet)
router.register(r'facility-billing-units', FacilityBillingUnitViewSet)
router.register(r'power-cuts', PowerCutViewSet)
router.register(r'complaints', PowerHouseComplaintViewSet)
router.register(r'users', UserViewSet, basename='user')

from .views_reports import (
    DGBillReportAPIView, EBBillReportAPIView, CategoryBillReportAPIView,
    MonthWiseSummaryAPIView, PowerCutReportAPIView, PowerHouseComplaintReportAPIView
)

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reports/dg-bill/', DGBillReportAPIView.as_view(), name='dg-bill-report'),
    path('reports/eb-bill/', EBBillReportAPIView.as_view(), name='eb-bill-report'),
    path('reports/category-bill/', CategoryBillReportAPIView.as_view(), name='category-bill-report'),
    path('reports/month-wise-summary/', MonthWiseSummaryAPIView.as_view(), name='month-wise-summary'),
    path('reports/power-cut-details/', PowerCutReportAPIView.as_view(), name='power-cut-details'),
    path('reports/complaints/', PowerHouseComplaintReportAPIView.as_view(), name='complaints-report'),
]
