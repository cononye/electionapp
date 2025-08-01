import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from results.models import Agent, Party

class Command(BaseCommand):
    help = 'Creates a new agent'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username for the agent')
        parser.add_argument('password', type=str, help='The password for the agent')
        parser.add_argument('party_acronym', type=str, help='The acronym of the party the agent belongs to')
        parser.add_argument('--code', type=str, help='A unique code for the agent. If not provided, a random one will be generated.')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        party_acronym = options['party_acronym']
        unique_code = options['code'] or secrets.token_hex(16)

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User with username "{username}" already exists.'))
            return

        try:
            party = Party.objects.get(acronym=party_acronym)
        except Party.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Party with acronym "{party_acronym}" does not exist.'))
            return

        # Create the user
        user = User.objects.create_user(username=username, password=password)

        # Create the agent
        agent = Agent.objects.create(user=user, party=party, unique_code=unique_code)

        self.stdout.write(self.style.SUCCESS(f'Successfully created agent "{username}" with code "{unique_code}"'))
