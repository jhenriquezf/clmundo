# travel/monitoring.py
import logging
from django.utils import timezone
from .models import TripSegment

# Configurar logger
logger = logging.getLogger('clmundo')

def log_segment_status_change(segment, old_status, new_status):
    """Log cambios de estado de segmentos"""
    logger.info(
        f"Segment {segment.id} status changed: {old_status} -> {new_status} "
        f"for customer {segment.trip.customer.user.email}"
    )

def check_system_health():
    """Verificar salud del sistema"""
    today = timezone.now().date()
    
    # Verificar segmentos sin actualizar
    stale_segments = TripSegment.objects.filter(
        scheduled_datetime__date=today,
        status='pending',
        scheduled_datetime__lt=timezone.now()
    )
    
    if stale_segments.exists():
        logger.warning(f"Found {stale_segments.count()} stale segments")
    
    return {
        'stale_segments': stale_segments.count(),
        'total_segments_today': TripSegment.objects.filter(
            scheduled_datetime__date=today
        ).count()
    }
