# health.py - Agregar esto a tu app travel/views.py o crear un archivo nuevo

from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import redis

def health_check(request):
    """
    Endpoint de health check para monitoreo
    """
    status = {
        'status': 'healthy',
        'database': 'unknown',
        'redis': 'unknown',
    }
    http_status = 200

    # Check database
    try:
        connection.ensure_connection()
        status['database'] = 'connected'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
        http_status = 503

    # Check Redis
    try:
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        status['redis'] = 'connected'
    except Exception as e:
        status['redis'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
        http_status = 503

    return JsonResponse(status, status=http_status)


# Agregar a urls.py:
# from travel.views import health_check  # o donde lo hayas puesto
# 
# urlpatterns = [
#     ...
#     path('health/', health_check, name='health'),
#     ...
# ]
