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
        user = request.user

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

        return ResultSubmission.objects.create(**submission_data)
