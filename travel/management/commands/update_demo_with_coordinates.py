# travel/management/commands/update_demo_with_coordinates.py
from django.core.management.base import BaseCommand
from travel.models import TripSegment
from travel.services.google_maps import GoogleMapsService

class Command(BaseCommand):
    help = 'Actualizar datos demo con coordenadas y mejorar información'

    def handle(self, *args, **options):
        maps_service = GoogleMapsService()
        
        # Actualizar segmentos con mejores ubicaciones
        segments_updates = [
            {
                'service_name': 'Vuelo SCL → PMC',
                'pickup_location': 'Aeropuerto El Tepual, Puerto Montt, Chile',
                'destination_location': 'Puerto Varas, Chile'
            },
            {
                'service_name': 'Traslado Aeropuerto',
                'pickup_location': 'Aeropuerto El Tepual, Puerto Montt, Chile', 
                'destination_location': 'Hotel Cabañas del Lago, Luis Wellmann 195, Puerto Varas, Chile'
            },
            {
                'service_name': 'Check-in Hotel',
                'pickup_location': 'Hotel Cabañas del Lago, Luis Wellmann 195, Puerto Varas, Chile',
                'destination_location': 'Hotel Cabañas del Lago, Luis Wellmann 195, Puerto Varas, Chile'
            },
            {
                'service_name': 'City Tour Puerto Varas',
                'pickup_location': 'Hotel Cabañas del Lago, Luis Wellmann 195, Puerto Varas, Chile',
                'destination_location': 'Centro de Puerto Varas, Chile'
            }
        ]
        
        updated_count = 0
        for update in segments_updates:
            try:
                segment = TripSegment.objects.get(service__name=update['service_name'])
                segment.pickup_location = update['pickup_location']
                segment.destination_location = update['destination_location']
                
                # Obtener coordenadas si Google Maps está disponible
                if maps_service.is_available():
                    coords = maps_service.geocode_address(segment.pickup_location)
                    if coords:
                        segment.pickup_latitude = coords['lat']
                        segment.pickup_longitude = coords['lng']
                
                segment.save()
                updated_count += 1
                self.stdout.write(f"✅ Actualizado: {segment.service.name}")
                
            except TripSegment.DoesNotExist:
                self.stdout.write(f"❌ No encontrado: {update['service_name']}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Actualizados {updated_count} segmentos con nueva información')
        )