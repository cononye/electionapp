from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import Agent

class AgentCodeBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # The authenticate method can be called with request=None, for example
        # by the test client's login() method. We should handle this gracefully.
        if request is None:
            return None

        agent_code = request.headers.get('X-Agent-Code')
        if not agent_code:
            return None

        try:
            agent = Agent.objects.get(unique_code=agent_code)
            return agent.user
        except Agent.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
