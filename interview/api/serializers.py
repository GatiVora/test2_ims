from rest_framework import serializers
from account.models import User
from account.api.serializers import UserSerializer
from interview.models import Job, ApplicationRound, JobApplication, Feedback, InterviewRound


class JobSerializer(serializers.ModelSerializer):
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'department', 'position', 'is_open', 'application_count']
    
    def get_application_count(self, obj):
        return obj.applications.count()

class JobApplicationSerializer(serializers.ModelSerializer):

    job_details = JobSerializer(source='job', read_only=True)
    candidate_details = UserSerializer(source='candidate', read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'job_details','candidate', 'candidate_details','applied_on', 'status', 'is_selected']

    def validate(self, data):
        if JobApplication.objects.filter(job=data['job'], candidate=data['candidate']).exists():
            raise serializers.ValidationError("Candidate has already applied to this job.")
        return data
    
class InterviewRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewRound
        fields = ['id', 'round_type']

class ApplicationRoundSerializer(serializers.ModelSerializer):
    application_details = JobApplicationSerializer(source='application', read_only=True)
    interviewer_details = UserSerializer(source='interviewer', read_only=True)
    round_details = InterviewRoundSerializer(source='round', read_only=True)

    class Meta:
        model = ApplicationRound
        fields = ['id','application','application_details','round','round_details','scheduled_time','interviewer','interviewer_details','duration']

    def validate_scheduled_time(self, value):
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("Cannot schedule interviews in the past.")
        return value
    
class FeedbackSerializer(serializers.ModelSerializer):
    application_round_details = ApplicationRoundSerializer(source='application_round', read_only=True)
    class Meta:
        model = Feedback
        fields = ['id', 'application_round','application_round_details', 'comments', 'rating']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        feedback = super().create(validated_data)

        app = feedback.application_round.application
        total_rounds = app.rounds.count()
        completed_feedbacks = Feedback.objects.filter(application_round__application=app).count()

        if total_rounds == completed_feedbacks:
            app.status = 'closed'
            app.save()

        return feedback

class JobApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['status']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
