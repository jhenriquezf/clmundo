# travel/templatetags/travel_extras.py
from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def status_color(status):
    """Retorna color CSS para estado"""
    colors = {
        'confirmed': 'green',
        'pending': 'yellow',
        'en_route': 'blue', 
        'completed': 'gray',
        'cancelled': 'red',
        'delayed': 'orange'
    }
    return colors.get(status, 'gray')

@register.filter
def service_icon(service_type):
    """Retorna ícono Feather para tipo de servicio"""
    icons = {
        'flight': 'plane',
        'transfer': 'truck',
        'hotel': 'home',
        'tour': 'camera',
        'activity': 'mountain'
    }
    return icons.get(service_type, 'circle')

@register.filter
def time_until(datetime_obj):
    """Calcula tiempo restante hasta un evento"""
    if not datetime_obj:
        return "Sin programar"
    
    now = timezone.now()
    diff = datetime_obj - now
    
    if diff.total_seconds() < 0:
        return "Ya pasó"
    elif diff.days > 0:
        return f"En {diff.days} día{'s' if diff.days > 1 else ''}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"En {hours} hora{'s' if hours > 1 else ''}"
    else:
        minutes = diff.seconds // 60
        return f"En {minutes} minuto{'s' if minutes > 1 else ''}"