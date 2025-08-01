from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Agent

class AgentCodeAuthentication(BaseAuthentication):
    """
    Custom DRF authentication class for agents.
    Authenticates a user based on a unique code sent in the 'X-Agent-Code' header.
    """
    def authenticate(self, request):
        agent_code = request.headers.get('X-Agent-Code')

        if not agent_code:
            # No agent code provided.
            # Let other authentication classes (like SessionAuthentication) handle the request.
            return None

        try:
            agent = Agent.objects.select_related('user').get(unique_code=agent_code)
        except Agent.DoesNotExist:
            # Raise an exception if the code is provided but invalid.
            raise AuthenticationFailed('Invalid agent code.')

        if not agent.user:
            # This should not happen if data integrity is maintained, but it's a good check.
            raise AuthenticationFailed('Agent is not associated with a user.')

        # If authentication is successful, return the user and auth token (None in this case).
        return (agent.user, None)
