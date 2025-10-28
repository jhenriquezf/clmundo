# travel/context_processors.py

from datetime import date

def travel_context(request):
    """Contexto global mejorado para templates"""
    from datetime import date
    from django.conf import settings
    
    context = {
        # APIs disponibles
        'google_maps_available': bool(getattr(settings, 'GOOGLE_MAPS_API_KEY', False)),
        'whatsapp_available': bool(getattr(settings, 'TWILIO_ACCOUNT_SID', False)),
        
        # Configuración por defecto
        'default_location': getattr(settings, 'DEFAULT_LOCATION', {
            'lat': -41.2985,
            'lng': -72.9781,
            'city': 'Puerto Varas'
        })
    }
    
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            context['unread_notifications'] = customer.notifications.filter(read=False).count()
            
            # Incidencias no resueltas
            from .models import Incident
            context['unread_incidents'] = Incident.objects.filter(
                segment__trip__customer=customer,
                status__in=['open', 'in_progress']
            ).count()
            
            # Viaje activo
            today = date.today()
            active_trip = customer.trips.filter(
                start_date__lte=today,
                end_date__gte=today
            ).first()
            context['active_trip'] = active_trip
            
        except Exception:
            context['unread_notifications'] = 0
            context['unread_incidents'] = 0
            context['active_trip'] = None
    
    return context