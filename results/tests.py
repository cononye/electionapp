import io
from PIL import Image
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import PollingUnit, Party, Agent, ResultSubmission

class ResultSubmissionAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test case"""
        cls.party = Party.objects.create(name="Progressive Party", acronym="PP")
        cls.polling_unit = PollingUnit.objects.create(
            name="Test PU",
            unit_code="PU001",
            state="Test State",
            lga="Test LGA",
            ward="Test Ward"
        )

    def setUp(self):
        """Set up data for each test"""
        self.client = APIClient()

        # Create a public user
        self.public_user = User.objects.create_user(username='publicuser', password='password123')

        # Create an agent user and agent
        self.agent_user = User.objects.create_user(username='agentuser', password='password123')
        self.agent = Agent.objects.create(
            user=self.agent_user,
            party=self.party,
            unique_code='secretagentcode'
        )

        # Create a dummy image for upload
        self.image = self.generate_dummy_image()

    def generate_dummy_image(self):
        """Generates a dummy image for testing file uploads"""
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'jpeg')
        file.name = 'test.jpg'
        file.seek(0)
        return file

    def test_unauthenticated_submission_fails(self):
        """Test that an unauthenticated user cannot submit results"""
        url = reverse('submit-result')
        data = {
            'polling_unit_code': self.polling_unit.unit_code,
            'scores': '{"PP": 100}',
            'result_form_image': self.image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_user_submission_succeeds(self):
        """Test that an authenticated public user can submit results"""
        self.client.login(username='publicuser', password='password123')
        url = reverse('submit-result')
        data = {
            'polling_unit_code': self.polling_unit.unit_code,
            'scores': '{"PP": 110}',
            'result_form_image': self.image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        submission = ResultSubmission.objects.get(submitted_by_user=self.public_user)
        self.assertEqual(submission.source, 'public')
        self.assertEqual(submission.polling_unit, self.polling_unit)
        self.assertEqual(submission.scores['PP'], 110)

    def test_agent_submission_succeeds(self):
        """Test that an authenticated agent can submit results using the code"""
        self.client.credentials(HTTP_X_AGENT_CODE='secretagentcode')
        url = reverse('submit-result')
        data = {
            'polling_unit_code': self.polling_unit.unit_code,
            'scores': '{"PP": 120}',
            'result_form_image': self.image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        submission = ResultSubmission.objects.get(submitted_by_agent=self.agent)
        self.assertEqual(submission.source, 'agent')
        self.assertEqual(submission.polling_unit, self.polling_unit)
        self.assertEqual(submission.scores['PP'], 120)

    def test_submission_with_invalid_pu_code_fails(self):
        """Test submission fails with a non-existent polling unit code"""
        self.client.login(username='publicuser', password='password123')
        url = reverse('submit-result')
        data = {
            'polling_unit_code': 'INVALIDCODE',
            'scores': '{"PP": 130}',
            'result_form_image': self.image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('polling_unit_code', response.data)

    def test_index_view_returns_200(self):
        """Test that the index view returns a 200 OK status code and correct title."""
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "<title>Election Results Tracker</title>")
