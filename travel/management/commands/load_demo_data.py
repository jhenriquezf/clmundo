# travel/management/commands/load_demo_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
from travel.models import Customer, Trip, Service, TripSegment, Incident

class Command(BaseCommand):
    help = 'Carga datos de demostración para ClMundo con fechas actualizadas'

    def handle(self, *args, **options):
        self.stdout.write("Cargando datos de demostración...")
        
        # Crear o obtener usuario demo
        user, created = User.objects.get_or_create(
            username='ana.silva',
            defaults={
                'first_name': 'Ana',
                'last_name': 'Silva',
                'email': 'ana.silva@email.com'
            }
        )
        if created:
            user.set_password('demo1234')  # Establecer contraseña
            user.save()
            self.stdout.write("✅ Usuario demo creado")
        else:
            self.stdout.write("✅ Usuario demo ya existe")
        
        # Crear o obtener cliente
        customer, created = Customer.objects.get_or_create(
            user=user,
            defaults={
                'phone': '+56 9 1234 5678',
                'emergency_contact': 'Pedro Silva +56 9 8765 4321'
            }
        )
        if created:
            self.stdout.write("✅ Cliente demo creado")
        else:
            self.stdout.write("✅ Cliente demo ya existe")

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
            if created:
                self.stdout.write(f"✅ Servicio creado: {service.name}")
            else:
                self.stdout.write(f"✅ Servicio ya existe: {service.name}")

        # Crear viaje con fechas actuales
        today = timezone.now().date()
        trip, created = Trip.objects.get_or_create(
            customer=customer,
            destination='Puerto Varas',
            defaults={
                'start_date': today,
                'end_date': today + timedelta(days=3),
                'total_passengers': 2,
                'status': 'confirmed'
            }
        )
        if created:
            self.stdout.write("✅ Viaje demo creado")
        else:
            # Actualizar fechas del viaje existente
            trip.start_date = today
            trip.end_date = today + timedelta(days=3)
            trip.save()
            self.stdout.write("✅ Fechas del viaje actualizadas")

        # Eliminar segmentos existentes para evitar duplicados
        TripSegment.objects.filter(trip=trip).delete()
        self.stdout.write("✅ Segmentos antiguos eliminados")

        # Crear segmentos del viaje con fechas y horas actualizadas
        now = timezone.now()
        segments_data = [
            {
                'service': services[0],  # Vuelo
                'scheduled_datetime': now.replace(hour=10, minute=20, second=0, microsecond=0),
                'pickup_location': 'Terminal 1 SCL',
                'destination_location': 'Aeropuerto El Tepual',
                'provider': 'SKY Airline',
                'status': 'completed'
            },
            {
                'service': services[1],  # Traslado
                'scheduled_datetime': now.replace(hour=11, minute=0, second=0, microsecond=0),
                'pickup_location': 'Terminal Aeropuerto',
                'destination_location': 'Hotel Cabañas del Lago',
                'provider': 'Juan Pérez',
                'provider_contact': '+56 9 8888 7777',
                'status': 'en_route'
            },
            {
                'service': services[2],  # Check-in
                'scheduled_datetime': now.replace(hour=12, minute=0, second=0, microsecond=0),
                'pickup_location': 'Recepción hotel',
                'status': 'confirmed'
            },
            {
                'service': services[3],  # City Tour
                'scheduled_datetime': now.replace(hour=16, minute=0, second=0, microsecond=0),
                'pickup_location': 'Lobby hotel',
                'destination_location': 'Centro Puerto Varas',
                'provider': 'Tours del Sur',
                'status': 'pending'
            },
            {
                'service': services[4],  # Saltos del Petrohué
                'scheduled_datetime': (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0),
                'pickup_location': 'Lobby hotel',
                'destination_location': 'Saltos del Petrohué',
                'status': 'confirmed'
            },
            {
                'service': services[5],  # Volcán Osorno
                'scheduled_datetime': (now + timedelta(days=2)).replace(hour=9, minute=0, second=0, microsecond=0),
                'pickup_location': 'Lobby hotel',
                'destination_location': 'Centro de Ski Volcán Osorno',
                'status': 'confirmed'
            }
        ]

        for i, segment_data in enumerate(segments_data):
            voucher_code = f'AT-PV-{now.strftime("%y%m%d")}-{i+1:03d}'
            
            segment = TripSegment.objects.create(
                trip=trip,
                service=segment_data['service'],
                scheduled_datetime=segment_data['scheduled_datetime'],
                pickup_location=segment_data.get('pickup_location', ''),
                destination_location=segment_data.get('destination_location', ''),
                provider=segment_data.get('provider', ''),
                provider_contact=segment_data.get('provider_contact', ''),
                status=segment_data.get('status', 'pending'),
                voucher_code=voucher_code
            )
            self.stdout.write(f"✅ Segmento creado: {segment.service.name} - {segment.scheduled_datetime}")

        self.stdout.write(
            self.style.SUCCESS('Datos de demostración cargados exitosamente')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Puedes iniciar sesión con usuario: ana.silva / demo1234')
        )