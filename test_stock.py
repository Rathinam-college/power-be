import os
import django
import sys
sys.path.append('d:\\PowerTracker')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'powertracker.settings')
django.setup()

from meters.models import Genset

for g in Genset.objects.all():
    print(f'Genset: {g.name}, Stock: {g.current_stock}')
