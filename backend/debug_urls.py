
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import get_resolver
from django.utils.module_loading import import_string

print(f"Base Dir: {settings.BASE_DIR}")
print(f"Root URLConf: {settings.ROOT_URLCONF}")

resolver = get_resolver()
print(f"URL Patterns: {resolver.url_patterns}")

try:
    import evidence_engine.urls
    print(f"evidence_engine.urls file: {evidence_engine.urls.__file__}")
except ImportError:
    print("Could not import evidence_engine.urls")

# Print all urlpatterns
for p in resolver.url_patterns:
    print(p)
