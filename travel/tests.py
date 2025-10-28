# travel/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, datetime, timedelta
from .models import Customer, Trip, Service, TripSegment

class TravelViewsTest(TestCase):
    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.customer = Customer.objects.create(
            user=self.user,
            phone='+56 9 1234 5678'
        )
        
        # Crear servicio de prueba
        self.service = Service.objects.create(
            name='Test Service',
            service_type='tour',
            description='Test tour service'
        )
        
        # Crear viaje de prueba
        self.trip = Trip.objects.create(
            customer=self.customer,
            destination='Test Destination',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3)
        )
        
        # Crear segmento de prueba
        self.segment = TripSegment.objects.create(
            trip=self.trip,
            service=self.service,
            scheduled_datetime=datetime.now(),
            voucher_code='TEST-001'
        )
        
        self.client = Client()

    def test_landing_page_access(self):
        """Test acceso a página de bienvenida"""
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ClMundo')

    def test_home_requires_login(self):
        """Test que home requiere autenticación"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_home_with_login(self):
        """Test acceso a home con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.first_name)

    def test_segment_detail_access(self):
        """Test acceso a detalles de segmento"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('segment_detail', args=[self.segment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service.name)

    def test_operations_dashboard_staff_only(self):
        """Test que dashboard de operaciones requiere staff"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('operations'))
        self.assertEqual(response.status_code, 302)  # Redirect due to no staff permissions

    def test_operations_dashboard_with_staff(self):
        """Test dashboard de operaciones con usuario staff"""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('operations'))
        self.assertEqual(response.status_code, 200)

