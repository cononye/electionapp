from django.core.management.base import BaseCommand
from results.models import PollingUnit, ResultSubmission, Party
from django.db.models import Count

class Command(BaseCommand):
    help = 'Aggregates election results from verified submissions.'

    def handle(self, *args, **options):
        self.stdout.write('Starting result aggregation...')

        # For now, we will consider submissions from agents as "verified".
        # A more advanced implementation would use the discrepancy data.
        verified_submissions = ResultSubmission.objects.filter(source='agent')

        # Aggregate scores by party
        party_scores = {}
        for party in Party.objects.all():
            party_scores[party.acronym] = 0

        for submission in verified_submissions:
            for party_acronym, score in submission.scores.items():
                if party_acronym in party_scores:
                    party_scores[party_acronym] += score

        self.stdout.write(self.style.SUCCESS('National Results:'))
        for party, score in party_scores.items():
            self.stdout.write(f'{party}: {score}')

        # Aggregate results by state
        state_scores = {}
        for submission in verified_submissions:
            state = submission.polling_unit.state
            if state not in state_scores:
                state_scores[state] = {p.acronym: 0 for p in Party.objects.all()}

            for party_acronym, score in submission.scores.items():
                if party_acronym in state_scores[state]:
                    state_scores[state][party_acronym] += score

        self.stdout.write(self.style.SUCCESS('\nState-level Results:'))
        for state, scores in state_scores.items():
            self.stdout.write(f'\n--- {state} ---')
            for party, score in scores.items():
                self.stdout.write(f'{party}: {score}')

        self.stdout.write(self.style.SUCCESS('\nAggregation complete.'))