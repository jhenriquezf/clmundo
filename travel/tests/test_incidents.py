# travel/tests/test_incidents.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from travel.models import Customer, Trip, Service, TripSegment, Incident

class IncidentSystemTest(TestCase):
    def setUp(self):
        # Crear usuario cliente
        self.client_user = User.objects.create_user(
            username='cliente_test',
            email='cliente@test.com',
            password='test123',
            first_name='Cliente',
            last_name='Test'
        )
        
        self.customer = Customer.objects.create(
            user=self.client_user,
            phone='+56 9 1234 5678'
        )
        
        # Crear usuario staff
        self.staff_user = User.objects.create_user(
            username='staff_test',
            email='staff@test.com',
            password='staff123',
            is_staff=True
        )
        
        # Crear datos de prueba
        self.service = Service.objects.create(
            name='Test Tour',
            service_type='tour',
            description='Tour de prueba'
        )
        
        self.trip = Trip.objects.create(
            customer=self.customer,
            destination='Test Destination',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=3)
        )
        
        self.segment = TripSegment.objects.create(
            trip=self.trip,
            service=self.service,
            scheduled_datetime=timezone.now(),
            voucher_code='TEST-001'
        )
        
        self.client_obj = Client()

    def test_report_incident_success(self):
        """Test reportar incidencia correctamente"""
        self.client_obj.login(username='cliente_test', password='test123')
        
        incident_data = {
            'title': 'Problema de prueba',
            'description': 'Descripción del problema',
            'category': 'transport',
            'severity': 'medium',
            'location': 'Hotel Test',
            'incident_datetime': timezone.now().isoformat(),
            'affected_passengers': 2,
            'reporter_contact': '+56 9 8765 4321'
        }
        
        response = self.client_obj.post(
            reverse('report_incident', args=[self.segment.id]),
            data=incident_data
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se creó la incidencia
        incident = Incident.objects.filter(segment=self.segment).first()
        self.assertIsNotNone(incident)
        self.assertEqual(incident.title, 'Problema de prueba')
        self.assertEqual(incident.status, 'open')

    def test_incident_list_view(self):
        """Test vista de lista de incidencias"""
        self.client_obj.login(username='cliente_test', password='test123')
        
        # Crear incidencia de prueba
        Incident.objects.create(
            segment=self.segment,
            title='Test Incident',
            description='Test description',
            category='transport',
            severity='medium'
        )
        
        response = self.client_obj.get(reverse('incident_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Incident')

    def test_staff_incident_dashboard(self):
        """Test dashboard de staff"""
        self.client_obj.login(username='staff_test', password='staff123')
        
        response = self.client_obj.get(reverse('staff_incidents_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard de Incidencias')

    def test_incident_resolution(self):
        """Test resolución de incidencia por staff"""
        self.client_obj.login(username='staff_test', password='staff123')
        
        # Crear incidencia
        incident = Incident.objects.create(
            segment=self.segment,
            title='Test Incident',
            description='Test description',
            status='open'
        )
        
        # Resolver incidencia
        resolution_data = {
            'status': 'resolved',
            'resolution_notes': 'Problema resuelto correctamente',
            'internal_notes': 'Notas internas'
        }
        
        response = self.client_obj.post(
            reverse('staff_incident_detail', args=[incident.id]),
            data=resolution_data
        )
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se actualizó
        incident.refresh_from_db()
        self.assertEqual(incident.status, 'resolved')
        self.assertIsNotNone(incident.resolved_at)