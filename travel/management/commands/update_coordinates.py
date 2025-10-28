from django.core.management.base import BaseCommand
from travel.models import TripSegment
from travel.services.google_maps import GoogleMapsService

class Command(BaseCommand):
    help = 'Actualizar coordenadas de segmentos usando Google Maps'

    def handle(self, *args, **options):
        maps_service = GoogleMapsService()
        
        if not maps_service.is_available():
            self.stdout.write(self.style.ERROR('Google Maps API no disponible'))
            return
        
        segments = TripSegment.objects.filter(
            pickup_latitude__isnull=True,
            pickup_location__isnull=False
        ).exclude(pickup_location='')
        
        updated_count = 0
        for segment in segments:
            coords = maps_service.geocode_address(segment.pickup_location)
            if coords:
                segment.pickup_latitude = coords['lat']
                segment.pickup_longitude = coords['lng']
                segment.save(update_fields=['pickup_latitude', 'pickup_longitude'])
                updated_count += 1
                
                self.stdout.write(f"✅ {segment.service.name}: {coords['formatted_address']}")
            else:
                self.stdout.write(f"❌ No se pudo geocodificar: {segment.pickup_location}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Actualizados {updated_count} segmentos con coordenadas')
        )