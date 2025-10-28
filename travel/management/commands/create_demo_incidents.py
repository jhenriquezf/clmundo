# travel/management/commands/create_demo_incidents.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from travel.models import TripSegment, Incident, User

class Command(BaseCommand):
    help = 'Crear incidencias demo para testing'

    def handle(self, *args, **options):
        # Obtener segmentos existentes
        segments = TripSegment.objects.all()
        if not segments:
            self.stdout.write(self.style.ERROR('No hay segmentos. Ejecuta setup_demo primero'))
            return
        
        # Crear usuarios staff si no existen
        staff_user, created = User.objects.get_or_create(
            username='soporte1',
            defaults={
                'first_name': 'Ana',
                'last_name': 'Soporte',
                'email': 'soporte1@andestravel.com',
                'is_staff': True
            }
        )
        
        # Datos demo para incidencias
        incident_data = [
            {
                'title': 'Bus llegó 30 minutos tarde',
                'description': 'El bus del city tour llegó con 30 minutos de retraso al hotel. Esto causó que perdiéramos tiempo del tour programado.',
                'category': 'transport',
                'severity': 'medium',
                'status': 'resolved',
                'location': 'Hotel Cabañas del Lago',
                'affected_passengers': 2,
                'resolution_notes': 'Se extendió el tour 30 minutos adicionales sin costo. Se ofreció descuento del 10% en próxima actividad.'
            },
            {
                'title': 'Problema con voucher en recepción',
                'description': 'Al hacer check-in en el hotel, no reconocían nuestro voucher y decían que no tenían reserva.',
                'category': 'accommodation',
                'severity': 'high',
                'status': 'in_progress',
                'location': 'Recepción Hotel',
                'affected_passengers': 2,
                'assigned_to': staff_user
            },
            {
                'title': 'Guía del tour no hablaba español claramente',
                'description': 'Durante el city tour, el guía tenía dificultades para comunicarse en español, lo que hizo difícil entender las explicaciones.',
                'category': 'service_quality',
                'severity': 'low',
                'status': 'open',
                'location': 'Puerto Varas centro',
                'affected_passengers': 2
            },
            {
                'title': 'Cancelación por mal tiempo sin aviso',
                'description': 'La excursión al Volcán Osorno fue cancelada por mal tiempo pero no nos avisaron hasta llegar al punto de encuentro.',
                'category': 'weather',
                'severity': 'high',
                'status': 'resolved',
                'location': 'Lobby hotel',
                'affected_passengers': 2,
                'resolution_notes': 'Se reprogramó la excursión para el día siguiente con traslado gratuito adicional.'
            }
        ]
        
        # Crear incidencias
        for i, data in enumerate(incident_data):
            segment = segments[min(i, len(segments)-1)]
            
            # Calcular fecha de incidente (últimos 3 días)
            incident_date = timezone.now() - timedelta(days=random.randint(0, 3), 
                                                      hours=random.randint(0, 23))
            
            incident = Incident.objects.create(
                segment=segment,
                title=data['title'],
                description=data['description'],
                category=data['category'],
                severity=data['severity'],
                status=data['status'],
                location=data.get('location', ''),
                incident_datetime=incident_date,
                affected_passengers=data['affected_passengers'],
                reporter_contact='+56 9 1234 5678',
                resolution_notes=data.get('resolution_notes', ''),
                assigned_to=data.get('assigned_to'),
                reported_at=incident_date + timedelta(minutes=random.randint(5, 60))
            )
            
            # Si está resuelto, agregar fecha de resolución
            if incident.status == 'resolved':
                incident.resolved_at = incident.reported_at + timedelta(
                    hours=random.randint(2, 24)
                )
                # Agregar calificación aleatoria
                incident.customer_satisfaction = random.randint(3, 5)
                incident.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Creadas {len(incident_data)} incidencias demo')
        )
        self.stdout.write('🔗 Accesos disponibles:')
        self.stdout.write('👤 Cliente - Ver incidencias: /my-incidents/')
        self.stdout.write('⚙️ Staff - Dashboard: /staff/incidents/')