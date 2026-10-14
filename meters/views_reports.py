from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from decimal import Decimal
import calendar
import datetime
from .models import (
    Category, Genset, GensetReading, DieselEntry, DieselRate,
    MeterConfig, MeterReading, FacilityBillingUnit, PowerCut,
    PowerHouseComplaint
)
from .serializers import MeterReadingSerializer


class DGBillReportAPIView(APIView):
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not month or not year:
            return Response({"error": "month and year are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"error": "Invalid month or year"}, status=status.HTTP_400_BAD_REQUEST)
            
        _, last_day = calendar.monthrange(year, month)
        end_of_month = datetime.date(year, month, last_day)

        # 1. Active Diesel Price
        diesel_rate_obj = DieselRate.objects.filter(
            effective_date__lte=end_of_month
        ).order_by('-effective_date').first()
        active_diesel_price = (
            diesel_rate_obj.price_per_liter if diesel_rate_obj
            else Decimal('0.00')
        )

        # Find all gensets
        gensets = Genset.objects.all().order_by('name')

        results = []
        for genset in gensets:
            # Total Diesel Consumed by this genset in this month
            diesel_entries = DieselEntry.objects.filter(
                genset=genset,
                entry_date__year=year,
                entry_date__month=month
            )
            total_diesel_consumed = (
                diesel_entries.aggregate(Sum('consumed_liters'))
                ['consumed_liters__sum'] or Decimal('0.00')
            )
            
            # Find companies connected to this genset via MeterConfig
            # active in this month or earlier
            configs = MeterConfig.objects.filter(genset=genset)
            company_ids = configs.values_list('company_id', flat=True).distinct()

            # Find GensetReadings for these companies in the specified month
            genset_readings = GensetReading.objects.filter(
                company_id__in=company_ids,
                reading_date__year=year,
                reading_date__month=month
            ).select_related('company')

            # Total Genset Units for this genset
            total_genset_units = (
                genset_readings.aggregate(Sum('reading_value'))
                ['reading_value__sum'] or Decimal('0.00')
            )
            
            # Calculate Per Unit Rate
            # Formula: (Total Diesel Consumed * Active Diesel Price)
            # / Total Genset Units
            per_unit_rate = Decimal('0.00')
            if total_genset_units > 0:
                per_unit_rate = (
                    (total_diesel_consumed * active_diesel_price) /
                    total_genset_units
                )

            companies_data = []
            for reading in genset_readings:
                units = reading.reading_value
                amount = units * per_unit_rate

                # Liters = Amount / Active Diesel Price
                liters = Decimal('0.00')
                if active_diesel_price > 0:
                    liters = amount / active_diesel_price

                companies_data.append({
                    "company_id": reading.company.id,
                    "company_name": reading.company.name,
                    "previous_reading": str(reading.previous_reading),
                    "current_reading": str(reading.current_reading),
                    "units": str(units),
                    "per_unit_rate": str(round(per_unit_rate, 2)),
                    "amount": str(round(amount, 2)),
                    "liters": str(round(liters, 2))
                })

            results.append({
                "genset_id": genset.id,
                "genset_name": genset.name,
                "total_diesel_consumed": str(total_diesel_consumed),
                "total_genset_units": str(total_genset_units),
                "active_diesel_price": str(active_diesel_price),
                "per_unit_rate": str(round(per_unit_rate, 2)),
                "companies": companies_data
            })

        return Response(results, status=status.HTTP_200_OK)


class EBBillReportAPIView(APIView):
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not month or not year:
            return Response({"error": "month and year are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"error": "Invalid month or year"}, status=status.HTTP_400_BAD_REQUEST)
            
        readings = MeterReading.objects.filter(
            reading_date__year=year,
            reading_date__month=month
        ).select_related('company', 'company__block', 'company__category')
        
        serializer = MeterReadingSerializer(readings, many=True)
        readings_data = serializer.data
        
        blocks_map = {}
        for r_data in readings_data:
            block_name = r_data.get('block_name') or "Unassigned Block"
            if block_name not in blocks_map:
                blocks_map[block_name] = {
                    "block_name": block_name,
                    "total_net_amount": 0.0,
                    "readings": []
                }
            blocks_map[block_name]["readings"].append(r_data)
            
            # Aggregate block totals
            net_amt = r_data.get('net_amount')
            if net_amt is not None:
                blocks_map[block_name]["total_net_amount"] += float(net_amt)
                
        # Format for decimal places
        results = []
        for b_name in sorted(blocks_map.keys()):
            blocks_map[b_name]["total_net_amount"] = round(
                blocks_map[b_name]["total_net_amount"], 2
            )
            results.append(blocks_map[b_name])
            
        return Response(results, status=status.HTTP_200_OK)

class CategoryBillReportAPIView(APIView):
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not month or not year:
            return Response({"error": "month and year are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"error": "Invalid month or year"}, status=status.HTTP_400_BAD_REQUEST)
            
        readings = MeterReading.objects.filter(
            reading_date__year=year,
            reading_date__month=month
        ).select_related('company', 'company__category')
        
        serializer = MeterReadingSerializer(readings, many=True)
        readings_data = serializer.data
        
        categories_map = {}
        for r_data in readings_data:
            category_name = r_data.get('category_name') or "Unassigned Category"
            if category_name not in categories_map:
                categories_map[category_name] = {
                    "category_name": category_name,
                    "total_net_amount": 0.0,
                    "readings": []
                }
            categories_map[category_name]["readings"].append(r_data)
            
            # Aggregate category totals
            net_amt = r_data.get('net_amount')
            if net_amt is not None:
                categories_map[category_name]["total_net_amount"] += float(net_amt)
                
        # Format for decimal places
        results = []
        for c_name in sorted(categories_map.keys()):
            categories_map[c_name]["total_net_amount"] = round(
                categories_map[c_name]["total_net_amount"], 2
            )
            results.append(categories_map[c_name])
            
        return Response(results, status=status.HTTP_200_OK)

class MonthWiseSummaryAPIView(APIView):
    def get(self, request):
        try:
            months_count = int(request.query_params.get('months', 6))
        except ValueError:
            months_count = 6
            
        end_month_param = request.query_params.get('end_month')
        end_year_param = request.query_params.get('end_year')
        
        if end_month_param and end_year_param:
            try:
                current_month = int(end_month_param)
                current_year = int(end_year_param)
            except ValueError:
                today = datetime.date.today()
                current_year = today.year
                current_month = today.month
        else:
            today = datetime.date.today()
            current_year = today.year
            current_month = today.month
            
        months = []
        for i in range(months_count):
            m = current_month - i
            y = current_year
            while m <= 0:
                m += 12
                y -= 1
            months.append((y, m))
        
        months.reverse() # Oldest to newest
        
        categories = Category.objects.all().order_by('name')
        
        response_data = []
        for category in categories:
            cat_months_data = []
            for y, m in months:
                # Total Units & Total Cost
                readings = MeterReading.objects.filter(
                    company__category=category,
                    reading_date__year=y,
                    reading_date__month=m
                ).select_related('company')
                
                total_units = readings.aggregate(Sum('reading_value'))['reading_value__sum'] or Decimal('0.00')
                
                # For cost, we need to calculate net_amount for each reading
                # This could be expensive, but MeterReadingSerializer is currently our source of truth
                total_cost = Decimal('0.00')
                if readings.exists():
                    serializer = MeterReadingSerializer(readings, many=True)
                    for r_data in serializer.data:
                        net_amt = r_data.get('net_amount')
                        if net_amt:
                            total_cost += Decimal(str(net_amt))
                
                # Fetch Billing Unit active for this month
                # Effective date should be on or before the end of this month
                _, last_day = calendar.monthrange(y, m)
                end_of_month = datetime.date(y, m, last_day)
                
                billing_unit = FacilityBillingUnit.objects.filter(
                    category=category,
                    effective_date__lte=end_of_month
                ).order_by('-effective_date').first()
                
                unit_count = billing_unit.unit_count if billing_unit else 1 # Avoid division by zero
                unit_type = billing_unit.unit_type if billing_unit else "Units"
                
                units_per_billing = total_units / Decimal(str(unit_count)) if unit_count > 0 else Decimal('0.00')
                cost_per_billing = total_cost / Decimal(str(unit_count)) if unit_count > 0 else Decimal('0.00')
                
                cat_months_data.append({
                    "month_name": calendar.month_name[m][:3] + "'" + str(y), # e.g. Sept'2025
                    "year": y,
                    "month": m,
                    "total_units": float(total_units),
                    "total_cost": float(total_cost),
                    "unit_count": unit_count,
                    "unit_type": unit_type,
                    "units_per_billing": float(round(units_per_billing, 2)),
                    "cost_per_billing": float(round(cost_per_billing, 2))
                })
            
            response_data.append({
                "category_id": category.id,
                "category_name": category.name,
                "data": cat_months_data
            })
            
        return Response(response_data, status=status.HTTP_200_OK)

class PowerCutReportAPIView(APIView):
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not month or not year:
            return Response({"error": "month and year are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"error": "Invalid month or year"}, status=status.HTTP_400_BAD_REQUEST)
            
        power_cuts = PowerCut.objects.filter(
            date__year=year,
            date__month=month
        ).order_by('date', 'start_time')
        
        results = []
        total_seconds = 0
        for pc in power_cuts:
            start = datetime.datetime.combine(datetime.date.today(), pc.start_time)
            end = datetime.datetime.combine(datetime.date.today(), pc.end_time)
            
            diff = end - start
            if diff.total_seconds() < 0:
                diff += datetime.timedelta(days=1)
            
            seconds = int(diff.total_seconds())
            total_seconds += seconds
            
            h = seconds // 3600
            m = (seconds % 3600) // 60
            duration_str = f"{h:02d}:{m:02d}"
            
            results.append({
                "id": pc.id,
                "date": pc.date,
                "start_time": pc.start_time.strftime('%H:%M'),
                "end_time": pc.end_time.strftime('%H:%M'),
                "duration": duration_str
            })
            
        total_h = total_seconds // 3600
        total_m = (total_seconds % 3600) // 60
        total_duration_str = f"{total_h:02d}:{total_m:02d}"
        
        return Response({
            "power_cuts": results,
            "total_duration": total_duration_str
        }, status=status.HTTP_200_OK)


class PowerHouseComplaintReportAPIView(APIView):
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not month or not year:
            return Response({"error": "month and year are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"error": "Invalid month or year"}, status=status.HTTP_400_BAD_REQUEST)

        complaints = PowerHouseComplaint.objects.filter(
            date__year=year,
            date__month=month
        ).order_by('date', 'start_time')

        results = []
        total_seconds = 0
        for comp in complaints:
            # Only calculate duration for closed complaints that have an end time
            if comp.is_closed and comp.end_time:
                start = datetime.datetime.combine(datetime.date.today(), comp.start_time)
                end = datetime.datetime.combine(datetime.date.today(), comp.end_time)

                diff = end - start
                if diff.total_seconds() < 0:
                    diff += datetime.timedelta(days=1)

                seconds = int(diff.total_seconds())
                total_seconds += seconds

            results.append({
                "id": comp.id,
                "date": comp.date,
                "location": (comp.block.name if comp.block else "Unknown Block") if comp.is_block_location else comp.manual_location,
                "complaint": comp.complaint_request,
                "is_closed": comp.is_closed,
                "start_time": comp.start_time.strftime('%H:%M'),
                "end_time": comp.end_time.strftime('%H:%M') if comp.end_time else None,
                "duration": comp.duration
            })

        total_h = total_seconds // 3600
        total_m = (total_seconds % 3600) // 60
        total_duration_str = f"{total_h:02d}:{total_m:02d}"

        return Response({
            "complaints": results,
            "total_duration": total_duration_str
        }, status=status.HTTP_200_OK)
