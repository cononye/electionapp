from results.models import Party, PollingUnit, Agent, ResultSubmission
from django.contrib.auth.models import User

def run():
    # Clean up existing data
    Party.objects.all().delete()
    PollingUnit.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

    # Create Parties
    pa = Party.objects.create(name="Party A", acronym="PA")
    pb = Party.objects.create(name="Party B", acronym="PB")
    pc = Party.objects.create(name="Party C", acronym="PC")

    # Create Polling Units
    pu1 = PollingUnit.objects.create(name="LGA Primary School", unit_code="PU001", state="Kano", lga="Kano", ward="Ward 1")
    pu2 = PollingUnit.objects.create(name="Town Hall", unit_code="PU002", state="Kano", lga="Kano", ward="Ward 2")
    pu3 = PollingUnit.objects.create(name="Central Market", unit_code="PU003", state="Lagos", lga="Ikeja", ward="Ward A")

    # Create Agents
    agent_user1 = User.objects.create_user(username="agent1", password="password")
    agent1 = Agent.objects.create(user=agent_user1, party=pa, unique_code="AGENT001")

    agent_user2 = User.objects.create_user(username="agent2", password="password")
    agent2 = Agent.objects.create(user=agent_user2, party=pb, unique_code="AGENT002")

    # Create Result Submissions
    ResultSubmission.objects.create(
        polling_unit=pu1,
        submitted_by_agent=agent1,
        source='agent',
        scores={'PA': 150, 'PB': 100, 'PC': 25}
    )
    ResultSubmission.objects.create(
        polling_unit=pu2,
        submitted_by_agent=agent1,
        source='agent',
        scores={'PA': 200, 'PB': 120, 'PC': 30}
    )
    ResultSubmission.objects.create(
        polling_unit=pu3,
        submitted_by_agent=agent2,
        source='agent',
        scores={'PA': 180, 'PB': 250, 'PC': 50}
    )

    print("Test data has been set up successfully.")