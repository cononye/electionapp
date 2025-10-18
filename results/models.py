from django.db import models
from django.contrib.auth.models import User

class PollingUnit(models.Model):
    name = models.CharField(max_length=255)
    unit_code = models.CharField(max_length=50, unique=True)
    state = models.CharField(max_length=100)
    lga = models.CharField(max_length=100)  # Local Government Area
    ward = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.unit_code})"

class Party(models.Model):
    name = models.CharField(max_length=100, unique=True)
    acronym = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.acronym

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True)
    unique_code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Agent {self.user.username} for {self.party.acronym if self.party else 'N/A'}"

class ResultSubmission(models.Model):
    SOURCE_CHOICES = (
        ('agent', 'Agent'),
        ('public', 'Public'),
    )

    polling_unit = models.ForeignKey(PollingUnit, on_delete=models.CASCADE, related_name='submissions')
    submitted_by_agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    result_form_image = models.ImageField(upload_to='result_forms/')
    scores = models.JSONField()
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)
    ocr_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Submission for {self.polling_unit} at {self.submitted_at}"

class Discrepancy(models.Model):
    STATUS_CHOICES = (
        ('unresolved', 'Unresolved'),
        ('resolved', 'Resolved'),
    )

    polling_unit = models.ForeignKey(PollingUnit, on_delete=models.CASCADE, related_name='discrepancies')
    agent_submission = models.ForeignKey(ResultSubmission, on_delete=models.CASCADE, related_name='agent_discrepancies')
    public_submissions = models.ManyToManyField(ResultSubmission, related_name='public_discrepancies')
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unresolved')
    created_at = models.DateTimeField(auto_now_add=True)
    ocr_results = models.JSONField(default=dict)

    def __str__(self):
        return f"Discrepancy for {self.polling_unit}"
