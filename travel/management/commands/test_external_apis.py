# travel/management/commands/test_external_apis.py
from django.core.management.base import BaseCommand
from travel.services.google_maps import GoogleMapsService
from travel.services.whatsapp import WhatsAppService

class Command(BaseCommand):
    help = 'Probar conexiones con APIs externas'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Probando conexiones con APIs externas...\n")
        
        # Probar Google Maps
        maps_service = GoogleMapsService()
        if maps_service.is_available():
            self.stdout.write("✅ Google Maps API: Conectado")
            
            # Probar geocoding
            test_address = "Puerto Varas, Chile"
            coords = maps_service.geocode_address(test_address)
            if coords:
                self.stdout.write(f"   Geocoding test: {test_address} → {coords['lat']}, {coords['lng']}")
            
            # Probar direcciones
            directions = maps_service.get_directions("Puerto Varas", "Puerto Montt")
            if directions:
                self.stdout.write(f"   Directions test: {directions['duration']}, {directions['distance']}")
            
            # Probar lugares cercanos
            places = maps_service.find_nearby_places(-41.2985, -72.9781, 'restaurant')
            self.stdout.write(f"   Places test: {len(places)} restaurantes encontrados")
            
        else:
            self.stdout.write("❌ Google Maps API: No configurado")
        
        # Probar WhatsApp
        whatsapp_service = WhatsAppService()
        if whatsapp_service.is_available():
            self.stdout.write("\n✅ WhatsApp API (Twilio): Conectado")
            self.stdout.write("   Para probar envío, usar: python manage.py test_whatsapp_send")
        else:
            self.stdout.write("\n❌ WhatsApp API: No configurado")
        
        self.stdout.write("\n📋 CONFIGURACIÓN:")
        self.stdout.write("   GOOGLE_MAPS_API_KEY: " + ("✅ Set" if maps_service.is_available() else "❌ Missing"))
        self.stdout.write("   TWILIO_ACCOUNT_SID: " + ("✅ Set" if whatsapp_service.is_available() else "❌ Missing"))
        self.stdout.write("   TWILIO_AUTH_TOKEN: " + ("✅ Set" if whatsapp_service.is_available() else "❌ Missing"))
