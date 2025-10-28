# travel/management/commands/setup_demo_cliente.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from travel.models import Customer, Trip, Service, TripSegment
import uuid

class Command(BaseCommand):
    help = 'Configurar datos demo para presentación de cliente - Oct 24-28, 2025'

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
            User.objects.filter(username__in=['ana.silva', 'juan.morales', 'operador']).delete()
            self.stdout.write(self.style.WARNING('Datos anteriores eliminados'))

        # Crear usuarios demo
        user1, created = User.objects.get_or_create(
            username='ana.silva',
            defaults={
                'first_name': 'Ana',
                'last_name': 'Silva',
                'email': 'ana.silva@email.com'
            }
        )
        if created:
            user1.set_password('demo1234')
            user1.save()
        
        customer1, created = Customer.objects.get_or_create(
            user=user1,
            defaults={
                'phone': '+56 9 1234 5678',
                'emergency_contact': 'Pedro Silva +56 9 8765 4321'
            }
        )

        # Segundo cliente para variedad
        user2, created = User.objects.get_or_create(
            username='juan.morales',
            defaults={
                'first_name': 'Juan',
                'last_name': 'Morales',
                'email': 'juan.morales@email.com'
            }
        )
        if created:
            user2.set_password('demo1234')
            user2.save()
        
        customer2, created = Customer.objects.get_or_create(
            user=user2,
            defaults={
                'phone': '+56 9 9876 5432',
                'emergency_contact': 'María Morales +56 9 5555 4444'
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
            # Vuelos
            ('Vuelo SCL → PMC', 'flight', 'Vuelo SKY H2 141 Santiago - Puerto Montt', 'Aeropuerto El Tepual', None),
            ('Vuelo PMC → SCL', 'flight', 'Vuelo SKY H2 144 Puerto Montt - Santiago', 'Aeropuerto El Tepual', None),
            
            # Traslados
            ('Traslado Aeropuerto - Hotel', 'transfer', 'Traslado privado desde aeropuerto', 'Puerto Varas', None),
            ('Traslado Hotel - Aeropuerto', 'transfer', 'Traslado privado hacia aeropuerto', 'Puerto Montt', None),
            
            # Hoteles
            ('Check-in Hotel Cumbres Patagónicas', 'hotel', 'Hotel 5 estrellas con spa', 'Imperial 0561, Puerto Varas', None),
            ('Check-out Hotel', 'hotel', 'Salida del hotel', 'Puerto Varas', None),
            
            # Tours y Actividades
            ('City Tour Puerto Varas', 'tour', 'Recorrido por puntos turísticos + Frutillar', 'Puerto Varas centro', 4.0),
            ('Excursión Saltos del Petrohué', 'activity', 'Visita a las cascadas y Lago Todos los Santos', 'Parque Nacional Vicente Pérez Rosales', 5.0),
            ('Volcán Osorno + Termas', 'activity', 'Centro de ski + Termas de Petrohué', 'Volcán Osorno', 7.0),
            ('Navegación Isla de Chiloé', 'activity', 'Tour completo por Chiloé: Castro, Dalcahue, iglesias patrimoniales', 'Puerto Montt', 9.0),
            ('Kayak en Lago Llanquihue', 'activity', 'Kayaking guiado con vista a volcanes', 'Playa Puerto Varas', 3.0),
            ('Trekking Parque Alerce Andino', 'activity', 'Caminata por bosque nativo milenario', 'Parque Nacional Alerce Andino', 6.0),
            
            # Servicios adicionales
            ('Cena Restaurante Mesa Tropera', 'dining', 'Cena típica patagónica', 'Santa Rosa 068, Puerto Varas', 2.0),
            ('Almuerzo con vista al lago', 'dining', 'Restaurant La Marca', 'Costanera Puerto Varas', 1.5),
        ]

        services = {}
        for name, service_type, description, location, duration in services_data:
            service, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    'service_type': service_type,
                    'description': description,
                    'location': location,
                    'duration_hours': duration
                }
            )
            services[name] = service
            if created:
                self.stdout.write(f"✅ Servicio creado: {name}")

        # Fechas específicas
        viernes_24 = datetime(2025, 10, 24)
        sabado_25 = datetime(2025, 10, 25)
        lunes_27 = datetime(2025, 10, 27)
        martes_28 = datetime(2025, 10, 28)

        # ============================================
        # VIAJE 1: Ana Silva (Viernes 24 - Martes 28)
        # ============================================
        trip1, created = Trip.objects.get_or_create(
            customer=customer1,
            destination='Puerto Varas',
            defaults={
                'start_date': viernes_24.date(),
                'end_date': martes_28.date(),
                'total_passengers': 2,
                'status': 'confirmed'
            }
        )
        if not created:
            trip1.start_date = viernes_24.date()
            trip1.end_date = martes_28.date()
            trip1.save()

        TripSegment.objects.filter(trip=trip1).delete()

        # VIERNES 24 - Llegada y City Tour
        segments_trip1 = [
            (services['Vuelo SCL → PMC'], viernes_24.replace(hour=10, minute=20), 'completed', 
             'Terminal 1 SCL', 'Aeropuerto El Tepual', 'SKY Airline', '+56 2 2352 5000'),
            
            (services['Traslado Aeropuerto - Hotel'], viernes_24.replace(hour=12, minute=0), 'completed',
             'Terminal Aeropuerto', 'Hotel Cumbres Patagónicas', 'TransferSur', '+56 9 8888 7777'),
            
            (services['Check-in Hotel Cumbres Patagónicas'], viernes_24.replace(hour=13, minute=0), 'completed',
             'Recepción hotel', 'Habitación 305', 'Hotel Cumbres', '+56 65 2233 444'),
            
            (services['City Tour Puerto Varas'], viernes_24.replace(hour=16, minute=0), 'completed',
             'Lobby hotel', 'Centro Puerto Varas', 'Tours del Sur', '+56 9 9999 8888'),
            
            (services['Cena Restaurante Mesa Tropera'], viernes_24.replace(hour=20, minute=30), 'completed',
             'Hotel', 'Mesa Tropera Restaurant', 'Reserva directa', '+56 65 2237 777'),
        ]

        # SÁBADO 25 - Petrohué Full Day
        segments_trip1.extend([
            (services['Excursión Saltos del Petrohué'], sabado_25.replace(hour=8, minute=30), 'confirmed',
             'Lobby hotel', 'Saltos del Petrohué', 'Andes Experience', '+56 9 7777 6666'),
            
            (services['Almuerzo con vista al lago'], sabado_25.replace(hour=14, minute=0), 'confirmed',
             'Saltos del Petrohué', 'Restaurant La Marca', 'Incluido en tour', ''),
        ])

        # LUNES 27 - Volcán Osorno + Termas
        segments_trip1.extend([
            (services['Volcán Osorno + Termas'], lunes_27.replace(hour=9, minute=0), 'pending',
             'Lobby hotel', 'Volcán Osorno', 'Patagonia Adventures', '+56 9 6666 5555'),
        ])

        # MARTES 28 - Chiloé Full Day y Regreso
        segments_trip1.extend([
            (services['Navegación Isla de Chiloé'], martes_28.replace(hour=7, minute=30), 'pending',
             'Lobby hotel', 'Castro, Chiloé', 'Chiloé Natural', '+56 9 5555 4444'),
            
            (services['Check-out Hotel'], martes_28.replace(hour=18, minute=0), 'pending',
             'Habitación', 'Recepción hotel', 'Hotel Cumbres', '+56 65 2233 444'),
            
            (services['Traslado Hotel - Aeropuerto'], martes_28.replace(hour=18, minute=30), 'pending',
             'Hotel Cumbres', 'Aeropuerto El Tepual', 'TransferSur', '+56 9 8888 7777'),
            
            (services['Vuelo PMC → SCL'], martes_28.replace(hour=20, minute=45), 'pending',
             'Aeropuerto El Tepual', 'Santiago', 'SKY Airline', '+56 2 2352 5000'),
        ])

        # Crear segmentos para Ana Silva
        for i, (service, scheduled_dt, status, pickup, destination, provider, contact) in enumerate(segments_trip1):
            scheduled_aware = timezone.make_aware(scheduled_dt)
            voucher_code = f"AT-{trip1.id:02d}-{scheduled_dt.strftime('%y%m%d')}-{i+1:03d}-{uuid.uuid4().hex[:4].upper()}"
            
            TripSegment.objects.create(
                trip=trip1,
                service=service,
                scheduled_datetime=scheduled_aware,
                pickup_location=pickup,
                destination_location=destination,
                status=status,
                voucher_code=voucher_code,
                provider=provider,
                provider_contact=contact
            )

        # ============================================
        # VIAJE 2: Juan Morales (Sábado 25 - Lunes 27)
        # ============================================
        trip2, created = Trip.objects.get_or_create(
            customer=customer2,
            destination='Puerto Varas',
            defaults={
                'start_date': sabado_25.date(),
                'end_date': lunes_27.date(),
                'total_passengers': 4,
                'status': 'confirmed'
            }
        )
        if not created:
            trip2.start_date = sabado_25.date()
            trip2.end_date = lunes_27.date()
            trip2.save()

        TripSegment.objects.filter(trip=trip2).delete()

        # SÁBADO 25 - Llegada tarde
        segments_trip2 = [
            (services['Vuelo SCL → PMC'], sabado_25.replace(hour=17, minute=30), 'confirmed',
             'Terminal 1 SCL', 'Aeropuerto El Tepual', 'SKY Airline', '+56 2 2352 5000'),
            
            (services['Traslado Aeropuerto - Hotel'], sabado_25.replace(hour=19, minute=0), 'confirmed',
             'Terminal Aeropuerto', 'Hotel Cumbres Patagónicas', 'TransferSur', '+56 9 8888 7777'),
            
            (services['Check-in Hotel Cumbres Patagónicas'], sabado_25.replace(hour=20, minute=0), 'confirmed',
             'Recepción hotel', 'Habitación 210', 'Hotel Cumbres', '+56 65 2233 444'),
        ]

        # LUNES 27 - Actividades y Regreso
        segments_trip2.extend([
            (services['Kayak en Lago Llanquihue'], lunes_27.replace(hour=9, minute=0), 'pending',
             'Playa Puerto Varas', 'Lago Llanquihue', 'Ko Kayak', '+56 9 4444 3333'),
            
            (services['Trekking Parque Alerce Andino'], lunes_27.replace(hour=14, minute=30), 'pending',
             'Lobby hotel', 'Parque Alerce Andino', 'Trekking Chile', '+56 9 3333 2222'),
            
            (services['Check-out Hotel'], lunes_27.replace(hour=19, minute=0), 'pending',
             'Habitación', 'Recepción hotel', 'Hotel Cumbres', '+56 65 2233 444'),
            
            (services['Traslado Hotel - Aeropuerto'], lunes_27.replace(hour=19, minute=30), 'pending',
             'Hotel Cumbres', 'Aeropuerto El Tepual', 'TransferSur', '+56 9 8888 7777'),
            
            (services['Vuelo PMC → SCL'], lunes_27.replace(hour=21, minute=15), 'pending',
             'Aeropuerto El Tepual', 'Santiago', 'SKY Airline', '+56 2 2352 5000'),
        ])

        # Crear segmentos para Juan Morales
        for i, (service, scheduled_dt, status, pickup, destination, provider, contact) in enumerate(segments_trip2):
            scheduled_aware = timezone.make_aware(scheduled_dt)
            voucher_code = f"AT-{trip2.id:02d}-{scheduled_dt.strftime('%y%m%d')}-{i+1:03d}-{uuid.uuid4().hex[:4].upper()}"
            
            TripSegment.objects.create(
                trip=trip2,
                service=service,
                scheduled_datetime=scheduled_aware,
                pickup_location=pickup,
                destination_location=destination,
                status=status,
                voucher_code=voucher_code,
                provider=provider,
                provider_contact=contact
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ DATOS DEMO CLIENTE CONFIGURADOS EXITOSAMENTE'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('📅 FECHAS CONFIGURADAS:'))
        self.stdout.write(f'   • Viernes 24 octubre 2025')
        self.stdout.write(f'   • Sábado 25 octubre 2025')
        self.stdout.write(f'   • Lunes 27 octubre 2025')
        self.stdout.write(f'   • Martes 28 octubre 2025')
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('👥 USUARIOS CREADOS:'))
        self.stdout.write(f'   👤 Cliente 1: ana.silva / demo1234')
        self.stdout.write(f'      Viaje: {viernes_24.strftime("%d/%m")} - {martes_28.strftime("%d/%m")} (2 pasajeros)')
        self.stdout.write(f'      Segmentos: {TripSegment.objects.filter(trip=trip1).count()}')
        self.stdout.write('')
        self.stdout.write(f'   👤 Cliente 2: juan.morales / demo1234')
        self.stdout.write(f'      Viaje: {sabado_25.strftime("%d/%m")} - {lunes_27.strftime("%d/%m")} (4 pasajeros)')
        self.stdout.write(f'      Segmentos: {TripSegment.objects.filter(trip=trip2).count()}')
        self.stdout.write('')
        self.stdout.write(f'   ⚙️ Operador: operador / ops123')
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('📊 ESTADÍSTICAS:'))
        self.stdout.write(f'   🎫 {len(services)} servicios creados')
        self.stdout.write(f'   ✈️ {TripSegment.objects.count()} segmentos totales')
        self.stdout.write(f'   📍 2 viajes activos')
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('🔗 URLS DISPONIBLES:'))
        self.stdout.write('   🏠 http://127.0.0.1:8000/')
        self.stdout.write('   📱 http://127.0.0.1:8000/home/')
        self.stdout.write('   ⚙️ http://127.0.0.1:8000/operations/')
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('💡 PRÓXIMOS PASOS:'))
        self.stdout.write('   1. python manage.py create_demo_incidents (crear incidencias)')
        self.stdout.write('   2. python manage.py update_demo_with_coordinates (si tienes Google Maps API)')
        self.stdout.write('')
