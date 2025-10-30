# travel/management/commands/populate_fresh_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from travel.models import Customer, Trip, Service, TripSegment
import uuid

class Command(BaseCommand):
    help = 'Crea un set de datos de demostración frescos para hoy (30 de Octubre)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todos los datos de demostración existentes antes de crear nuevos.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando creación de datos frescos para el demo...'))

        if options['reset']:
            self.stdout.write(self.style.WARNING('🗑️  Eliminando datos existentes (--reset activado)...'))
            TripSegment.objects.all().delete()
            Trip.objects.all().delete()
            Service.objects.all().delete()
            Customer.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('✅ Datos anteriores eliminados.'))

        # --- 1. Crear Usuarios ---
        self.stdout.write('👤 Creando usuarios...')
        user, created = User.objects.get_or_create(
            username='ana.silva',
            defaults={
                'first_name': 'Ana', 'last_name': 'Silva', 'email': 'ana.silva@email.com'
            }
        )
        if created:
            user.set_password('demo1234')
            user.save()

        customer, _ = Customer.objects.get_or_create(
            user=user,
            defaults={'phone': '+56 9 1234 5678', 'emergency_contact': 'Pedro Silva +56 9 8765 4321'}
        )
        self.stdout.write(self.style.SUCCESS(f'   -> Cliente "ana.silva" configurado.'))
        
        staff_user, created = User.objects.get_or_create(
            username='operador',
            defaults={
                'first_name': 'Carlos', 'last_name': 'Rojas', 'email': 'operador@clmundo.cl', 'is_staff': True
            }
        )
        if created:
            staff_user.set_password('ops123')
            staff_user.save()
        self.stdout.write(self.style.SUCCESS(f'   -> Operador "operador" configurado.'))

        # --- 2. Crear Servicios ---
        self.stdout.write('🛠️  Creando catálogo de servicios...')
        services_data = [
            {'name': 'Vuelo SCL → PMC', 'service_type': 'flight'},
            {'name': 'Traslado Aeropuerto - Hotel', 'service_type': 'transfer'},
            {'name': 'Check-in Hotel Cumbres', 'service_type': 'hotel'},
            {'name': 'City Tour Puerto Varas & Frutillar', 'service_type': 'tour'},
            {'name': 'Excursión Saltos del Petrohué', 'service_type': 'activity'},
            {'name': 'Volcán Osorno y Termas', 'service_type': 'activity'},
            {'name': 'Cena en Mesa Tropera', 'service_type': 'dining'},
            {'name': 'Traslado Hotel - Aeropuerto', 'service_type': 'transfer'},
            {'name': 'Vuelo PMC → SCL', 'service_type': 'flight'},
        ]
        
        services = {}
        for data in services_data:
            service, _ = Service.objects.get_or_create(name=data['name'], defaults=data)
            services[data['name']] = service
        self.stdout.write(self.style.SUCCESS(f'   -> {len(services)} servicios creados.'))

        # --- 3. Crear Viaje ---
        self.stdout.write('✈️  Creando viaje activo...')
        today = timezone.now().date()
        trip, _ = Trip.objects.get_or_create(
            customer=customer,
            destination='Puerto Varas y Alrededores',
            defaults={
                'start_date': today,
                'end_date': today + timedelta(days=3),
                'total_passengers': 2,
                'status': 'confirmed'
            }
        )
        TripSegment.objects.filter(trip=trip).delete() # Limpiar segmentos viejos de este viaje
        self.stdout.write(self.style.SUCCESS(f'   -> Viaje a {trip.destination} creado del {today.strftime("%d/%m")} al {trip.end_date.strftime("%d/%m")}.'))

        # --- 4. Crear Segmentos del Viaje ---
        self.stdout.write('🗓️  Generando itinerario detallado...')
        now = timezone.now()
        
        # Usamos un diccionario para mejor legibilidad
        segments_data = [
            # DÍA 1: Hoy (30 de Octubre)
            {'service': services['Vuelo SCL → PMC'], 'datetime': now.replace(hour=9, minute=30), 'status': 'completed', 'provider': 'LATAM Airlines'},
            {'service': services['Traslado Aeropuerto - Hotel'], 'datetime': now.replace(hour=11, minute=45), 'status': 'en_route', 'provider': 'TransferSur'},
            {'service': services['Check-in Hotel Cumbres'], 'datetime': now.replace(hour=13, minute=0), 'status': 'confirmed', 'provider': 'Hotel Cumbres'},
            {'service': services['City Tour Puerto Varas & Frutillar'], 'datetime': now.replace(hour=15, minute=0), 'status': 'pending', 'provider': 'Tours del Sur'},
            {'service': services['Cena en Mesa Tropera'], 'datetime': now.replace(hour=20, minute=30), 'status': 'pending', 'provider': 'Reserva #5543'},
            
            # DÍA 2: Mañana
            {'service': services['Excursión Saltos del Petrohué'], 'datetime': (now + timedelta(days=1)).replace(hour=8, minute=30), 'status': 'confirmed', 'provider': 'Andes Experience'},
            
            # DÍA 3: Pasado mañana
            {'service': services['Volcán Osorno y Termas'], 'datetime': (now + timedelta(days=2)).replace(hour=9, minute=0), 'status': 'confirmed', 'provider': 'Patagonia Adventures'},

            # DÍA 4: Regreso
            {'service': services['Traslado Hotel - Aeropuerto'], 'datetime': (now + timedelta(days=3)).replace(hour=11, minute=0), 'status': 'confirmed', 'provider': 'TransferSur'},
            {'service': services['Vuelo PMC → SCL'], 'datetime': (now + timedelta(days=3)).replace(hour=13, minute=45), 'status': 'confirmed', 'provider': 'SKY Airline'},
        ]

        for i, data in enumerate(segments_data):
            voucher = f"AT-{trip.id:02d}-{data['datetime'].strftime('%y%m%d')}-{i+1:03d}-{uuid.uuid4().hex[:4].upper()}"
            TripSegment.objects.create(
                trip=trip,
                service=data['service'],
                scheduled_datetime=data['datetime'],
                status=data['status'],
                provider=data['provider'],
                voucher_code=voucher
            )
        self.stdout.write(self.style.SUCCESS(f'   -> {len(segments_data)} segmentos creados para el itinerario.'))

        # --- Finalización ---
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('✅ ¡Datos de demostración frescos listos!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('Credenciales de acceso:')
        self.stdout.write(f'   👤 Cliente: ana.silva / demo1234')
        self.stdout.write(f'   ⚙️ Operador: operador / ops123')
        self.stdout.write('')
        self.stdout.write('Para ejecutar de nuevo y limpiar, usa:')
        self.stdout.write(self.style.HTTP_INFO('   python manage.py populate_fresh_data --reset'))
        self.stdout.write('')