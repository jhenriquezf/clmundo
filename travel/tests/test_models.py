# travel/tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from travel.models import Customer, Trip, Service, TripSegment, Incident

class ModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        self.customer = Customer.objects.create(
            user=self.user,
            phone='+56 9 1234 5678'
        )

    def test_customer_creation(self):
        """Test creación de customer"""
        self.assertEqual(str(self.customer), "Test User")
        self.assertEqual(self.customer.phone, '+56 9 1234 5678')

    def test_trip_creation(self):
        """Test creación de viaje"""
        trip = Trip.objects.create(
            customer=self.customer,
            destination='Puerto Varas',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3)
        )
        
        self.assertEqual(trip.customer, self.customer)
        self.assertEqual(trip.destination, 'Puerto Varas')

    def test_segment_voucher_code(self):
        """Test generación de código de voucher"""
        service = Service.objects.create(
            name='Test Service',
            service_type='tour'
        )
        
        trip = Trip.objects.create(
            customer=self.customer,
            destination='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1)
        )
        
        segment = TripSegment.objects.create(
            trip=trip,
            service=service,
            scheduled_datetime=datetime.now(),
            voucher_code='TEST-001'
        )
        
        self.assertEqual(segment.voucher_code, 'TEST-001')
