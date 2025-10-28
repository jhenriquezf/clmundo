# travel/api.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
from .models import TripSegment, Notification

@csrf_exempt
@login_required
def get_segment_status(request, segment_id):
    """Obtener estado actual de un segmento"""
    try:
        segment = TripSegment.objects.get(id=segment_id)
        return JsonResponse({
            'status': segment.status,
            'status_display': segment.get_status_display(),
            'last_updated': segment.actual_datetime or segment.scheduled_datetime
        })
    except TripSegment.DoesNotExist:
        return JsonResponse({'error': 'Segmento no encontrado'}, status=404)

@csrf_exempt
@login_required
def emergency_contact(request):
    """Endpoint para contacto de emergencia"""
    if request.method == 'POST':
        customer = request.user.customer
        data = json.loads(request.body)
        
        # Crear notificación de emergencia
        Notification.objects.create(
            customer=customer,
            title="Contacto de emergencia activado",
            message="Hemos recibido tu solicitud de emergencia. Te contactaremos inmediatamente."
        )
        
        # En producción aquí activarías protocolos de emergencia
        return JsonResponse({'success': True, 'message': 'Emergencia reportada'})
    
    return JsonResponse({'success': False})
