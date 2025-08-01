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
