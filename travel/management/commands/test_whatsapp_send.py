# travel/management/commands/test_whatsapp_send.py
from django.core.management.base import BaseCommand
from travel.services.whatsapp import WhatsAppService

class Command(BaseCommand):
    help = 'Probar envío de WhatsApp'

    def add_arguments(self, parser):
        parser.add_argument('phone', type=str, help='Número de teléfono (ej: +56912345678)')

    def handle(self, *args, **options):
        phone = options['phone']
        
        whatsapp_service = WhatsAppService()
        
        if not whatsapp_service.is_available():
            self.stdout.write(self.style.ERROR('WhatsApp service not configured'))
            return
        
        # Enviar mensaje de prueba
        result = whatsapp_service.send_message(
            phone,
            "🧪 Mensaje de prueba desde AndesTravel\n\nEste es un test de integración con WhatsApp Business API."
        )
        
        if result['success']:
            self.stdout.write(self.style.SUCCESS(f'Mensaje enviado exitosamente a {phone}'))
            self.stdout.write(f'Message SID: {result["message_sid"]}')
        else:
            self.stdout.write(self.style.ERROR(f'Error enviando mensaje: {result["error"]}'))
