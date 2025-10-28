# clmundo/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

def manifest_json(request):
    """Archivo manifest para PWA"""
    manifest = {
        "name": "AndesTravel",
        "short_name": "AndesTravel",
        "description": "Aplicación de viajes",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#0ea5e9",
        "icons": [
            {
                "src": "/static/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            }
        ]
    }
    return JsonResponse(manifest)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('manifest.json', manifest_json, name='manifest'),
    path('set_language/', set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('travel.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]