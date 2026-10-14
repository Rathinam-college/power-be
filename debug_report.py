import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from meters.models import PowerHouseComplaint

def debug_report():
    month = 2
    year = 2026
    print(f"Debugging report for {month}/{year}")
    
    complaints = PowerHouseComplaint.objects.filter(
        date__year=year,
        date__month=month
    ).order_by('date', 'start_time')
    
    print(f"Found {complaints.count()} complaints")
    
    total_seconds = 0
    for i, comp in enumerate(complaints):
        try:
            print(f"Processing complaint {i+1}: ID={comp.id}, start={comp.start_time}, end={comp.end_time}, is_closed={comp.is_closed}")
            
            if comp.is_closed and comp.end_time:
                start = datetime.datetime.combine(datetime.date.today(), comp.start_time)
                end = datetime.datetime.combine(datetime.date.today(), comp.end_time)

                diff = end - start
                if diff.total_seconds() < 0:
                    diff += datetime.timedelta(days=1)

                seconds = int(diff.total_seconds())
                total_seconds += seconds
                print(f"  Added {seconds} seconds")

            data = {
                "id": comp.id,
                "date": comp.date,
                "location": (comp.block.name if comp.block else "Unknown Block") if comp.is_block_location else comp.manual_location,
                "complaint": comp.complaint_request,
                "is_closed": comp.is_closed,
                "start_time": comp.start_time.strftime('%H:%M'),
                "end_time": comp.end_time.strftime('%H:%M') if comp.end_time else None,
                "duration": comp.duration
            }
            print(f"  Successfully serialized payload")
        except Exception as e:
            print(f"  ERROR on complaint {comp.id}: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_report()
