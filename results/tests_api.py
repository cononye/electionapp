from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Party, Agent
from django.contrib.auth.models import User

class DashboardAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.party = Party.objects.create(name="Test Party", acronym="TP")
        self.user = User.objects.create_user(username="testagent", password="password")
        self.agent = Agent.objects.create(user=self.user, party=self.party, unique_code="TESTAGENT001")

    def test_public_dashboard_endpoint(self):
        url = reverse('public-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_party_dashboard_endpoint_unauthenticated(self):
        url = reverse('party-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_party_dashboard_endpoint_authenticated(self):
        url = reverse('party-dashboard')
        self.client.credentials(HTTP_X_AGENT_CODE='TESTAGENT001')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['party_name'], 'Test Party')