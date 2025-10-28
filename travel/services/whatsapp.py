# travel/services/whatsapp.py
from twilio.rest import Client
from django.conf import settings
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Servicio para integración con WhatsApp vía Twilio"""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_whatsapp = settings.TWILIO_WHATSAPP_FROM
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
    
    def is_available(self) -> bool:
        """Verificar si el servicio está disponible"""
        return self.client is not None
    
    def send_message(self, to_phone: str, message: str, media_url: Optional[str] = None) -> Dict:
        """Enviar mensaje de WhatsApp"""
        if not self.is_available():
            logger.warning("WhatsApp service not available - missing credentials")
            return {'success': False, 'error': 'Service not configured'}
        
        try:
            # Formatear número de teléfono
            formatted_phone = self._format_phone(to_phone)
            
            message_params = {
                'from_': self.from_whatsapp,
                'to': f'whatsapp:{formatted_phone}',
                'body': message
            }
            
            # Agregar media si se proporciona
            if media_url:
                message_params['media_url'] = media_url
            
            message_obj = self.client.messages.create(**message_params)
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status
            }
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_template_message(self, to_phone: str, template_name: str, variables: Dict) -> Dict:
        """Enviar mensaje usando template pre-aprobado"""
        templates = {
            'itinerary_reminder': """
🌟 *AndesTravel - Recordatorio*

Hola {name}! 

Tu actividad de mañana:
📍 *{service_name}*
⏰ {datetime}
📍 {location}

Código voucher: *{voucher_code}*

¿Dudas? Responde a este mensaje 📱
            """,
            
            'incident_update': """
🔧 *Actualización de tu caso #{incident_id}*

Hola {name},

Tu incidencia "*{incident_title}*" ha sido actualizada:

Status: *{status}*
{resolution_notes}

Gracias por tu paciencia 🙏
            """,
            
            'emergency_contact': """
🚨 *AndesTravel - Soporte de Emergencia*

Hola {name},

Hemos recibido tu solicitud de contacto de emergencia.

Un miembro de nuestro equipo te contactará en los próximos 5 minutos.

Para emergencias médicas llama inmediatamente al 131 📞
            """
        }
        
        if template_name not in templates:
            return {'success': False, 'error': 'Template not found'}
        
        message = templates[template_name].format(**variables)
        return self.send_message(to_phone, message)
    
    def _format_phone(self, phone: str) -> str:
        """Formatear número de teléfono para WhatsApp"""
        # Remover espacios y caracteres especiales
        clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Si no tiene código de país, asumir Chile (+56)
        if not clean_phone.startswith('+'):
            if clean_phone.startswith('9'):
                clean_phone = '+56' + clean_phone
            elif clean_phone.startswith('569'):
                clean_phone = '+' + clean_phone
            else:
                clean_phone = '+56' + clean_phone
        
        return clean_phone
    
    def send_location(self, to_phone: str, lat: float, lng: float, name: str = "", address: str = "") -> Dict:
        """Enviar ubicación por WhatsApp"""
        message = f"📍 *{name}*\n{address}\n\nUbicación: https://maps.google.com/?q={lat},{lng}"
        return self.send_message(to_phone, message)
