# travel/tests/test_external_apis.py
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from travel.services.google_maps import GoogleMapsService
from travel.services.whatsapp import WhatsAppService

class ExternalAPIsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_google_maps_service_initialization(self):
        """Test inicialización del servicio de Google Maps"""
        service = GoogleMapsService()
        # Si no hay API key, should return False
        if not service.api_key:
            self.assertFalse(service.is_available())

    @patch('travel.services.google_maps.googlemaps.Client')
    def test_geocoding_success(self, mock_client):
        """Test geocoding exitoso"""
        mock_geocode = MagicMock()
        mock_geocode.return_value = [{
            'geometry': {'location': {'lat': -41.2985, 'lng': -72.9781}},
            'formatted_address': 'Puerto Varas, Chile',
            'place_id': 'test_place_id'
        }]
        
        mock_client_instance = MagicMock()
        mock_client_instance.geocode = mock_geocode
        mock_client.return_value = mock_client_instance
        
        service = GoogleMapsService()
        service.client = mock_client_instance
        
        result = service.geocode_address("Puerto Varas")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['lat'], -41.2985)
        self.assertEqual(result['lng'], -72.9781)

    def test_whatsapp_service_phone_formatting(self):
        """Test formateo de números de teléfono"""
        service = WhatsAppService()
        
        # Test número chileno
        formatted = service._format_phone('9 1234 5678')
        self.assertEqual(formatted, '+56912345678')
        
        # Test número con código de país
        formatted = service._format_phone('+56912345678')
        self.assertEqual(formatted, '+56912345678')

    @patch('travel.services.whatsapp.Client')
    def test_whatsapp_message_send(self, mock_client):
        """Test envío de mensaje WhatsApp"""
        mock_messages = MagicMock()
        mock_messages.create.return_value = MagicMock(
            sid='test_sid',
            status='queued'
        )
        
        mock_client_instance = MagicMock()
        mock_client_instance.messages = mock_messages
        mock_client.return_value = mock_client_instance
        
        service = WhatsAppService()
        service.client = mock_client_instance
        
        result = service.send_message('+56912345678', 'Test message')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['message_sid'], 'test_sid')