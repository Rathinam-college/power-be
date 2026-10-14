import os, sys, django
sys.path.append('d:\\PowerTracker')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'powertracker.settings')
django.setup()

from meters.models import DieselEntry
from django.db import connection

print("### Database Schema (meters_dieselentry)")
with connection.cursor() as cursor:
    if connection.vendor == 'sqlite':
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='meters_dieselentry'")
        res = cursor.fetchone()
        if res:
            print("```sql\n" + res[0] + "\n```")
    elif connection.vendor == 'postgresql':
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'meters_dieselentry'")
        print("| Column | Type |")
        print("|---|---|")
        for row in cursor.fetchall():
            print(f"| {row[0]} | {row[1]} |")

print("\n### Current Data in `meters_dieselentry`")
print("| ID | Genset | Entry Date | Opening | Purchased | Consumed | Closing | Created At |")
print("|---|---|---|---|---|---|---|---|")
for e in DieselEntry.objects.all():
    print(f"| {e.id} | {e.genset.name} | {e.entry_date} | {e.opening_stock} | {e.purchased_liters} | {e.consumed_liters} | {e.closing_stock} | {e.created_at.strftime('%Y-%m-%d %H:%M:%S')} |")
