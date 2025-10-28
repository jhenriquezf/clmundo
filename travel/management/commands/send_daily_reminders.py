# travel/management/commands/send_daily_reminders.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from travel.models import TripSegment
from travel.tasks import send_reminder_email

class Command(BaseCommand):
    help = 'Enviar recordatorios diarios para servicios próximos'

    def handle(self, *args, **options):
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        segments_tomorrow = TripSegment.objects.filter(
            scheduled_datetime__date=tomorrow,
            status__in=['confirmed', 'pending']
        )
        
        for segment in segments_tomorrow:
            send_reminder_email.delay(segment.id)
            self.stdout.write(f'Recordatorio programado para {segment.trip.customer.user.email}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Programados {segments_tomorrow.count()} recordatorios')
        )
