# travel/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import TripSegment, Incident, Notification
from django.utils import timezone

@receiver(post_save, sender=TripSegment)
def segment_status_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando cambia el estado de un segmento"""
    if not created and instance.status == 'en_route':
        Notification.objects.create(
            customer=instance.trip.customer,
            title=f"¡Tu {instance.service.get_service_type_display().lower()} está en camino!",
            message=f"{instance.service.name} llegará pronto. Revisa los detalles en tu itinerario."
        )
    elif not created and instance.status == 'completed':
        Notification.objects.create(
            customer=instance.trip.customer,
            title=f"{instance.service.name} completado",
            message=f"¡Esperamos que hayas disfrutado tu {instance.service.get_service_type_display().lower()}!"
        )

@receiver(post_save, sender=Incident)
def incident_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando se reporta una incidencia"""
    if created:
        Notification.objects.create(
            customer=instance.segment.trip.customer,
            title="Incidencia reportada",
            message=f"Hemos recibido tu reporte sobre '{instance.title}'. Te contactaremos pronto."
        )

@receiver(post_save, sender=Incident)
def incident_created_notification(sender, instance, created, **kwargs):
    """Notificar cuando se crea una nueva incidencia"""
    if created:
        # Notificación para el cliente
        Notification.objects.create(
            customer=instance.segment.trip.customer,
            title="Incidencia reportada",
            message=f"Hemos recibido tu reporte: '{instance.title}'. Código de seguimiento: #{instance.id}"
        )
        
        # TODO: Notificar al equipo de soporte vía email/SMS
        # send_staff_notification.delay(instance.id)

@receiver(pre_save, sender=Incident)
def incident_status_change_notification(sender, instance, **kwargs):
    """Notificar cambios de estado"""
    if instance.pk:  # Solo para incidencias existentes
        try:
            old_instance = Incident.objects.get(pk=instance.pk)
            
            # Si cambió el estado
            if old_instance.status != instance.status:
                status_messages = {
                    'in_progress': 'Nuestro equipo está trabajando en resolver tu caso',
                    'resolved': 'Tu incidencia ha sido resuelta',
                    'closed': 'Tu caso ha sido cerrado'
                }
                
                if instance.status in status_messages:
                    Notification.objects.create(
                        customer=instance.segment.trip.customer,
                        title=f"Actualización incidencia #{instance.id}",
                        message=status_messages[instance.status]
                    )
            
            # Si se resuelve, marcar fecha
            if (old_instance.status != 'resolved' and instance.status == 'resolved' 
                and not instance.resolved_at):
                instance.resolved_at = timezone.now()
                
        except Incident.DoesNotExist:
            pass