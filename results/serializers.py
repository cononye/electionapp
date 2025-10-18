from rest_framework import serializers
from .models import ResultSubmission, PollingUnit, Party

class ResultSubmissionSerializer(serializers.ModelSerializer):
    polling_unit_code = serializers.CharField(write_only=True)

    class Meta:
        model = ResultSubmission
        fields = ('polling_unit_code', 'scores', 'result_form_image')

    def create(self, validated_data):
        polling_unit_code = validated_data.pop('polling_unit_code')
        try:
            polling_unit = PollingUnit.objects.get(unit_code=polling_unit_code)
        except PollingUnit.DoesNotExist:
            raise serializers.ValidationError({'polling_unit_code': "Polling unit not found."})

        # Get the user from the request context
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        submission_data = {
            'polling_unit': polling_unit,
            **validated_data
        }

        if hasattr(user, 'agent'):
            submission_data['submitted_by_agent'] = user.agent
            submission_data['source'] = 'agent'
        else:
            submission_data['submitted_by_user'] = user
            submission_data['source'] = 'public'

        submission = ResultSubmission.objects.create(**submission_data)
        self.perform_ocr_on_image(submission)
        self.check_for_discrepancies(submission)
        return submission

    def perform_ocr_on_image(self, submission):
        try:
            import pytesseract
            from PIL import Image

            if not submission.result_form_image:
                return

            image = Image.open(submission.result_form_image)
            ocr_text = pytesseract.image_to_string(image)
            submission.ocr_text = ocr_text
            submission.save()

        except Exception as e:
            print(f"Error during OCR processing: {e}")

    def check_for_discrepancies(self, new_submission):
        from .models import Discrepancy

        polling_unit = new_submission.polling_unit
        agent_submissions = ResultSubmission.objects.filter(
            polling_unit=polling_unit, source='agent'
        ).order_by('submitted_at')

        public_submissions = ResultSubmission.objects.filter(
            polling_unit=polling_unit, source='public'
        ).order_by('submitted_at')

        if not agent_submissions.exists() or not public_submissions.exists():
            return

        agent_submission = agent_submissions.first()

        for public_submission in public_submissions:
            if agent_submission.scores != public_submission.scores:
                discrepancy, created = Discrepancy.objects.get_or_create(
                    polling_unit=polling_unit,
                    agent_submission=agent_submission,
                    defaults={
                        'description': 'Scores mismatch between agent and public submissions.',
                        'ocr_results': {
                            'agent_ocr': agent_submission.ocr_text,
                            'public_ocr': public_submission.ocr_text
                        }
                    }
                )
                if not created:
                    discrepancy.ocr_results['public_ocr'] = public_submission.ocr_text
                    discrepancy.save()

                discrepancy.public_submissions.add(public_submission)
