from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from .models import ResultSubmission
from .serializers import ResultSubmissionSerializer
from .drf_authentication import AgentCodeAuthentication

class SubmitResultView(CreateAPIView):
    """
    API view for submitting election results.

    This view is used by both authenticated agents (via X-Agent-Code header)
    and authenticated public users (via session).
    """
    queryset = ResultSubmission.objects.all()
    serializer_class = ResultSubmissionSerializer
    authentication_classes = [SessionAuthentication, AgentCodeAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        """
        Pass the request context to the serializer.
        """
        return {'request': self.request}

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Party, ResultSubmission, Discrepancy
from .serializers import ResultSubmissionSerializer

class PublicDashboardView(APIView):
    """
    Provides aggregated data for the public dashboard.
    """
    def get(self, request, *args, **kwargs):
        # This is a simplified aggregation for demonstration.
        # In a real-world scenario, this would use the aggregation engine.
        party_scores = {p.acronym: 0 for p in Party.objects.all()}
        submissions = ResultSubmission.objects.filter(source='agent') # Simplified: only use agent submissions
        for submission in submissions:
            for party, score in submission.scores.items():
                party_scores[party] += score

        disputed_pus = Discrepancy.objects.filter(status='unresolved').count()

        data = {
            'national_results': party_scores,
            'total_disputes': disputed_pus,
        }
        return Response(data)

class PartyDashboardView(APIView):
    """
    Provides detailed data for the party leader dashboard.
    Requires agent authentication.
    """
    authentication_classes = [AgentCodeAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        agent = request.user.agent
        party = agent.party

        agent_submissions = ResultSubmission.objects.filter(submitted_by_agent__party=party).count()
        unresolved_discrepancies = Discrepancy.objects.filter(
            agent_submission__submitted_by_agent__party=party,
            status='unresolved'
        ).count()

        data = {
            'party_name': party.name,
            'total_agent_submissions': agent_submissions,
            'unresolved_discrepancies': unresolved_discrepancies,
        }
        return Response(data)


def index_view(request):
    """
    Serves the main index.html page.
    """
    return render(request, 'index.html')

def public_dashboard_view(request):
    """
    Serves the public dashboard page.
    """
    return render(request, 'public_dashboard.html')

def party_dashboard_view(request):
    """
    Serves the party leader dashboard page.
    """
    return render(request, 'party_dashboard.html')

def agent_guide_view(request):
    """
    Serves the agent user guide.
    """
    return render(request, 'agent_guide.html')

def public_guide_view(request):
    """
    Serves the public user guide.
    """
    return render(request, 'public_guide.html')
