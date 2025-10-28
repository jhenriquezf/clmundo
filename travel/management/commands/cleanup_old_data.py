# travel/management/commands/cleanup_old_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from travel.models import Notification, Incident

class Command(BaseCommand):
    help = 'Limpiar datos antiguos del sistema'

    def handle(self, *args, **options):
        # Eliminar notificaciones leídas más antiguas a 30 días
        old_notifications = Notification.objects.filter(
            read=True,
            created_at__lt=timezone.now() - timedelta(days=30)
        )
        old_count = old_notifications.count()
        old_notifications.delete()
        
        # Archivar incidencias resueltas más antiguas a 90 días
        old_incidents = Incident.objects.filter(
            resolved_at__lt=timezone.now() - timedelta(days=90)
        )
        incidents_count = old_incidents.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Limpieza completada: {old_count} notificaciones y {incidents_count} incidencias procesadas'
            )
        )
