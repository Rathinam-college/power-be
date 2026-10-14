import os
import django
import json
from django.core import serializers

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Temporarily switch back to SQLite to dump data if needed, 
# but actually I should have done this BEFORE switching settings.py.
# However, I can just point to the sqlite engine manually for this script.

from django.conf import settings

# Original SQLite settings
sqlite_db = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), 'db.sqlite3'),
    }
}

# Override settings for this script
settings.DATABASES = sqlite_db

def dump_to_utf8():
    from django.apps import apps
    all_objects = []
    
    # Exclude contenttypes and auth.permissions to avoid conflicts
    excluded_apps = ['contenttypes', 'auth']
    
    for app_config in apps.get_app_configs():
        if app_config.label in excluded_apps:
            continue
        for model in app_config.get_models():
            objects = model.objects.all()
            all_objects.extend(list(objects))
    
    data = serializers.serialize("json", all_objects, indent=4)
    with open("data_utf8.json", "w", encoding="utf-8") as f:
        f.write(data)
    print("Exported data to data_utf8.json successfully.")

if __name__ == "__main__":
    dump_to_utf8()
