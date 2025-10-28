from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from travel.models import Customer, Trip, Service, TripSegment, Incident

class Command(BaseCommand):
    help = 'Crea datos de demostración para clmundo'

    def handle(self, *args, **options):
        # Crear usuario demo
        user, created = User.objects.get_or_create(
            username='ana.silva',
            defaults={
                'first_name': 'Ana',
                'last_name': 'Silva',
                'email': 'ana.silva@email.com'
            }
        )
        
        customer, created = Customer.objects.get_or_create(
            user=user,
            defaults={
                'phone': '+56 9 1234 5678',
                'emergency_contact': 'Pedro Silva +56 9 8765 4321'
            }
        )

        # Crear servicios
        services_data = [
            {
                'name': 'Vuelo SCL → PMC',
                'service_type': 'flight',
                'description': 'Vuelo SKY H2 141 Santiago - Puerto Montt',
                'location': 'Aeropuerto El Tepual'
            },
            {
                'name': 'Traslado Aeropuerto - Hotel',
                'service_type': 'transfer',
                'description': 'Traslado privado desde aeropuerto',
                'location': 'Puerto Varas'
            },
            {
                'name': 'Check-in Hotel Cabañas del Lago',
                'service_type': 'hotel',
                'description': 'Hotel 4 estrellas vista al lago',
                'location': 'Luis Wellmann 195, Puerto Varas'
            },
            {
                'name': 'City Tour Puerto Varas',
                'service_type': 'tour',
                'description': 'Recorrido por los principales puntos turísticos',
                'duration_hours': 3.0,
                'location': 'Puerto Varas centro'
            },
            {
                'name': 'Saltos del Petrohué',
                'service_type': 'activity',
                'description': 'Visita a las cascadas del río Petrohué',
                'duration_hours': 4.0,
                'location': 'Parque Nacional Vicente Pérez Rosales'
            },
            {
                'name': 'Volcán Osorno',
                'service_type': 'activity',
                'description': 'Excursión al centro de ski del volcán',
                'duration_hours': 6.0,
                'location': 'Centro de Ski Volcán Osorno'
            }
        ]

        services = []
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            services.append(service)

        # Crear viaje
        trip, created = Trip.objects.get_or_create(
            customer=customer,
            destination='Puerto Varas',
            defaults={
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=3),
                'total_passengers': 2,
                'status': 'confirmed'
            }
        )

        # Crear segmentos del viaje
        segments_data = [
            {
                'service': services[0],  # Vuelo
                'scheduled_datetime': datetime.combine(date.today(), datetime.min.time().replace(hour=10, minute=20)),
                'pickup_location': 'Terminal 1 SCL',
                'destination_location': 'Aeropuerto El Tepual',
                'provider': 'SKY Airline',
                'status': 'completed'
            },
            {
                'service': services[1],  # Traslado
                'scheduled_datetime': datetime.combine(date.today(), datetime.min.time().replace(hour=10, minute=45)),
                'pickup_location': 'Terminal Aeropuerto',
                'destination_location': 'Hotel Cabañas del Lago',
                'provider': 'Juan Pérez',
                'provider_contact': '+56 9 8888 7777',
                'status': 'confirmed'
            },
            {
                'service': services[2],  # Check-in
                'scheduled_datetime': datetime.combine(date.today(), datetime.min.time().replace(hour=15, minute=0)),
                'pickup_location': 'Recepción hotel',
                'status': 'pending'
            },
            {
                'service': services[3],  # City Tour
                'scheduled_datetime': datetime.combine(date.today(), datetime.min.time().replace(hour=16, minute=0)),
                'pickup_location': 'Lobby hotel',
                'destination_location': 'Centro Puerto Varas',
                'provider': 'Tours del Sur',
                'status': 'pending'
            },
            {
                'service': services[4],  # Saltos del Petrohué
                'scheduled_datetime': datetime.combine(date.today() + timedelta(days=1), datetime.min.time().replace(hour=8, minute=0)),
                'pickup_location': 'Lobby hotel',
                'destination_location': 'Saltos del Petrohué',
                'status': 'confirmed'
            },
            {
                'service': services[5],  # Volcán Osorno
                'scheduled_datetime': datetime.combine(date.today() + timedelta(days=2), datetime.min.time().replace(hour=9, minute=0)),
                'pickup_location': 'Lobby hotel',
                'destination_location': 'Centro de Ski Volcán Osorno',
                'status': 'confirmed'
            }
        ]

        for i, segment_data in enumerate(segments_data):
            segment_data['trip'] = trip
            segment_data['voucher_code'] = f'AT-PV-{date.today().strftime("%y%m%d")}-{i+1:03d}'
            
            segment, created = TripSegment.objects.get_or_create(
                trip=trip,
                service=segment_data['service'],
                scheduled_datetime=segment_data['scheduled_datetime'],
                defaults=segment_data
            )

        self.stdout.write(
            self.style.SUCCESS('Datos de demostración creados exitosamente')
        )
