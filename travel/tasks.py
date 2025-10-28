# travel/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import TripSegment, Customer, Incident

@shared_task
def send_incident_notification_email(incident_id):
    """Enviar notificación por email cuando se reporta una incidencia"""
    try:
        incident = Incident.objects.get(id=incident_id)
        customer = incident.segment.trip.customer
        
        # Email al cliente
        subject_client = f'Incidencia #{incident.id} recibida - AndesTravel'
        message_client = render_to_string('travel/emails/incident_reported.html', {
            'customer': customer,
            'incident': incident
        })
        
        send_mail(
            subject_client,
            message_client,
            'noreply@andestravel.com',
            [customer.user.email],
            html_message=message_client
        )
        
        # Email al equipo de soporte
        subject_staff = f'Nueva incidencia #{incident.id} - {incident.get_severity_display()}'
        message_staff = render_to_string('travel/emails/incident_staff_notification.html', {
            'incident': incident,
            'customer': customer
        })
        
        send_mail(
            subject_staff,
            message_staff,
            'noreply@andestravel.com',
            ['soporte@andestravel.com'],
            html_message=message_staff
        )
        
        return f'Emails enviados para incidencia #{incident.id}'
    except Exception as e:
        return f'Error enviando emails: {str(e)}'

@shared_task
def check_overdue_incidents():
    """Verificar y notificar incidencias vencidas"""
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    
    # Incidencias críticas > 4 horas sin resolver
    critical_overdue = Incident.objects.filter(
        status__in=['open', 'in_progress'],
        severity='critical',
        reported_at__lt=now - timedelta(hours=4),
        resolved_at__isnull=True
    )
    
    # Incidencias altas > 12 horas sin resolver
    high_overdue = Incident.objects.filter(
        status__in=['open', 'in_progress'],
        severity='high',
        reported_at__lt=now - timedelta(hours=12),
        resolved_at__isnull=True
    )
    
    overdue_incidents = list(critical_overdue) + list(high_overdue)
    
    for incident in overdue_incidents:
        # Enviar alerta al equipo
        send_mail(
            f'ALERTA: Incidencia vencida #{incident.id}',
            f'La incidencia #{incident.id} lleva {incident.response_time} horas sin resolver.\n'
            f'Severidad: {incident.get_severity_display()}\n'
            f'Cliente: {incident.segment.trip.customer.user.get_full_name()}\n'
            f'Título: {incident.title}',
            'alerts@andestravel.com',
            ['soporte@andestravel.com', 'supervisor@andestravel.com']
        )
    
    return f'Procesadas {len(overdue_incidents)} incidencias vencidas'


@shared_task
def send_reminder_email(segment_id):
    """Enviar recordatorio por email antes del servicio"""
    try:
        segment = TripSegment.objects.get(id=segment_id)
        customer = segment.trip.customer
        
        subject = f'Recordatorio: {segment.service.name}'
        message = render_to_string('travel/emails/reminder.html', {
            'customer': customer,
            'segment': segment
        })
        
        send_mail(
            subject,
            message,
            'noreply@clmundo.com',
            [customer.user.email],
            html_message=message
        )
        
        return f'Email enviado a {customer.user.email}'
    except Exception as e:
        return f'Error enviando email: {str(e)}'

@shared_task
def check_delayed_services():
    """Verificar servicios atrasados y notificar"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    delayed_segments = TripSegment.objects.filter(
        scheduled_datetime__lt=now - timedelta(minutes=15),
        status__in=['pending', 'confirmed']
    )
    
    for segment in delayed_segments:
        # Marcar como atrasado y notificar
        segment.status = 'delayed'
        segment.save()
        
        # Crear notificación
        from .models import Notification
        Notification.objects.create(
            customer=segment.trip.customer,
            title=f"Servicio atrasado: {segment.service.name}",
            message="Te contactaremos pronto con información actualizada."
        )