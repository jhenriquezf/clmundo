# travel/tests/test_views.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from travel.models import Customer

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.customer = Customer.objects.create(user=self.user)

    def test_landing_page(self):
        """Test página de landing"""
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)

    def test_home_redirect_when_not_logged_in(self):
        """Test redirección cuando no está autenticado"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_magic_link_login(self):
        """Test simulación de magic link"""
        response = self.client.post(reverse('magic_link_login'))
        self.assertEqual(response.status_code, 302)