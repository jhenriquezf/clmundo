# travel/management/commands/setup_demo.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, datetime, timedelta
from travel.models import Customer, Trip, Service, TripSegment
import uuid

class Command(BaseCommand):
    help = 'Configurar datos demo para AndesTravel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Eliminar datos existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Eliminando datos existentes...')
            TripSegment.objects.all().delete()
            Trip.objects.all().delete()
            Service.objects.all().delete()
            Customer.objects.all().delete()
            User.objects.filter(username__in=['ana.silva', 'operador']).delete()
            self.stdout.write(self.style.WARNING('Datos anteriores eliminados'))

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

        # Crear usuario operador
        staff_user, created = User.objects.get_or_create(
            username='operador',
            defaults={
                'first_name': 'Operador',
                'last_name': 'Sistema',
                'email': 'ops@andestravel.com',
                'is_staff': True
            }
        )
        if created:
            staff_user.set_password('ops123')
            staff_user.save()

        # Crear servicios
        services_data = [
            ('Vuelo SCL → PMC', 'flight', 'Vuelo SKY H2 141 Santiago - Puerto Montt', 'Aeropuerto El Tepual'),
            ('Traslado Aeropuerto', 'transfer', 'Traslado privado desde aeropuerto', 'Puerto Varas'),
            ('Check-in Hotel', 'hotel', 'Hotel Cabañas del Lago', 'Luis Wellmann 195, Puerto Varas'),
            ('City Tour Puerto Varas', 'tour', 'Recorrido por puntos turísticos', 'Puerto Varas centro'),
            ('Saltos del Petrohué', 'activity', 'Visita a las cascadas', 'Parque Nacional Vicente Pérez Rosales'),
            ('Volcán Osorno', 'activity', 'Excursión al volcán', 'Centro de Ski Volcán Osorno'),
        ]

        services = []
        for name, service_type, description, location in services_data:
            service, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    'service_type': service_type,
                    'description': description,
                    'location': location,
                    'duration_hours': 3.0 if service_type in ['tour', 'activity'] else None
                }
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

        # Limpiar segmentos existentes para este viaje
        TripSegment.objects.filter(trip=trip).delete()

        # Crear segmentos del viaje con timezone aware datetimes
        segments_data = [
            (services[0], '10:20', 'completed', 'Terminal 1 SCL'),  # Vuelo
            (services[1], '10:45', 'confirmed', 'Terminal Aeropuerto'),  # Traslado
            (services[2], '15:00', 'pending', 'Recepción hotel'),  # Check-in
            (services[3], '16:00', 'pending', 'Lobby hotel'),  # City Tour
            (services[4], '08:00', 'confirmed', 'Lobby hotel'),  # Petrohué (mañana)
            (services[5], '09:00', 'confirmed', 'Lobby hotel'),  # Osorno (pasado mañana)
        ]

        for i, (service, time_str, status, pickup_location) in enumerate(segments_data):
            hour, minute = map(int, time_str.split(':'))
            
            # Determinar el día basado en el índice
            if i <= 3:  # Hoy
                target_date = date.today()
            elif i == 4:  # Mañana
                target_date = date.today() + timedelta(days=1)
            else:  # Pasado mañana
                target_date = date.today() + timedelta(days=2)
            
            # Crear datetime con timezone aware
            scheduled_time = timezone.make_aware(
                datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
            )
            
            # Generar voucher code único
            voucher_code = f"AT-{trip.id:02d}-{target_date.strftime('%y%m%d')}-{i+1:03d}-{uuid.uuid4().hex[:4].upper()}"
            
            segment = TripSegment.objects.create(
                trip=trip,
                service=service,
                scheduled_datetime=scheduled_time,
                pickup_location=pickup_location,
                destination_location=service.location,
                status=status,
                voucher_code=voucher_code,
                provider='Juan Pérez' if service.service_type == 'transfer' else 'Tours del Sur',
                provider_contact='+56 9 8888 7777' if service.service_type == 'transfer' else '+56 9 9999 8888'
            )

        self.stdout.write(
            self.style.SUCCESS('✅ Datos demo configurados exitosamente!')
        )
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('USUARIOS CREADOS:'))
        self.stdout.write(f'👤 Cliente: ana.silva (usar Magic Link en /')
        self.stdout.write(f'🔧 Operador: operador / ops123 (para /operations/)')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('DATOS CREADOS:'))
        self.stdout.write(f'🎒 {services.__len__()} servicios')
        self.stdout.write(f'✈️ {TripSegment.objects.filter(trip=trip).count()} segmentos de viaje')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('URLS DISPONIBLES:'))
        self.stdout.write('🏠 http://127.0.0.1:8000/ (página principal)')
        self.stdout.write('📱 http://127.0.0.1:8000/home/ (después del login)')
        self.stdout.write('⚙️ http://127.0.0.1:8000/operations/ (dashboard operador)')