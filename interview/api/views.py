from rest_framework import status,generics,filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated

from account.api.serializers import UserSerializer
from account.models import User

from interview.models import Job,JobApplication,InterviewRound,ApplicationRound,Feedback
from interview.api.serializers import JobSerializer,JobApplicationSerializer,InterviewRoundSerializer,ApplicationRoundSerializer,FeedbackSerializer,JobApplicationStatusUpdateSerializer
from interview.api.permissions import IsAdmin, IsInterviewer, IsCandidate, IsAdminOrInterviewer, AdminFullInterviewerReadOnly


class JobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, AdminFullInterviewerReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'position', 'is_open'] #/jobs/?department=Python
    search_fields = ['title', 'description', 'department'] #/jobs/?search=developer 
    ordering_fields = ['created_at']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsAdmin]  # Only admin can create
        return super().get_permissions()


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, AdminFullInterviewerReadOnly]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsAdmin]  # Only admin can update/delete
        return super().get_permissions()

class JobApplicationsListView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrInterviewer]
    
    def get_queryset(self):
        job_id = self.kwargs.get('pk')
        return JobApplication.objects.filter(job_id=job_id) #to get all job applications for a specific job
    
class OpenJobsListView(generics.ListAPIView):
    queryset = Job.objects.filter(is_open = True)
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]  # All authenticated users can see open jobs

class JobApplicationListView(generics.ListCreateAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter]
    filterset_fields = ['status', 'is_selected', 'job']
    ordering_fields = ['applied_on', 'status']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsCandidate]  # Only candidates can create applications
        else:
            self.permission_classes = [IsAuthenticated, AdminFullInterviewerReadOnly]  # Admin and interviewer can view
        return super().get_permissions()
        
    def get_queryset(self):
        user = self.request.user
        if user.role == 'interviewer':
            # Interviewers can only see applications where they are assigned
            interviewer_rounds = ApplicationRound.objects.filter(interviewer=user).values_list('application_id', flat=True)
            return JobApplication.objects.filter(id__in=interviewer_rounds)
        elif user.role == 'candidate':
            # Candidates can only see their own applications
            return JobApplication.objects.filter(candidate=user)
        return super().get_queryset()  # Admin can see all

class JobApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobApplication.objects.all()
    permission_classes = [IsAuthenticated, AdminFullInterviewerReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH' and status in self.request.data:
            return JobApplicationStatusUpdateSerializer
        return JobApplicationSerializer

class SelectCandidateView(generics.UpdateAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]  # Only admins can select candidates

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'closed'
        instance.is_selected = True
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class MyApplicationsListView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]
    
    def get_queryset(self):
        user = self.request.user
        if user.role != 'candidate':
            return JobApplication.objects.none()
        return JobApplication.objects.filter(candidate=user)

class InterviewRoundListView(generics.ListCreateAPIView):
    queryset = InterviewRound.objects.all()
    serializer_class = InterviewRoundSerializer
    permission_classes = [IsAuthenticated, AdminFullInterviewerReadOnly]

class ApplicationRoundListView(generics.ListCreateAPIView):
    queryset = ApplicationRound.objects.all()
    serializer_class = ApplicationRoundSerializer
    permission_classes = [IsAuthenticated, AdminFullInterviewerReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['interviewer']
    ordering_fields = ['scheduled_time']

    def get_queryset(self):
        application_id = self.kwargs.get('pk')
        user = self.request.user
        queryset = ApplicationRound.objects.filter(application_id=application_id)
        
        # If interviewer, only show rounds they're assigned to
        if user.role == 'interviewer':
            queryset = queryset.filter(interviewer=user)
            
        return queryset

class ApplicationRoundDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ApplicationRound.objects.all()
    serializer_class = ApplicationRoundSerializer
    permission_classes = [IsAuthenticated, AdminFullInterviewerReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        
        # If interviewer, only allow access to their own interview rounds
        if user.role == 'interviewer':
            return ApplicationRound.objects.filter(interviewer=user)
        return ApplicationRound.objects.all()  # Admin can access all

class FeedbackCreateView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated, IsInterviewer]

    def perform_create(self, serializer):
        user = self.request.user
        application_round = serializer.validated_data['application_round']

        if application_round.interviewer != user and not user.is_staff:
            return Response(
                {'error': 'You cannot provide feedback'},
                status=status.HTTP_403_FORBIDDEN
            )

        feedback = serializer.save()
        
        # Trigger async task to send notification emails
        from interview.tasks import send_feedback_notification
        send_feedback_notification.delay(feedback.id)

class FeedbackListView(generics.ListAPIView):
    """
    Retrieve all feedback for:
    - a specific application round (/?application_round=<id>)
    - a specific job application (/?application=<id>)
    - a specific candidate (/?candidate=<id>)
    """
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated, AdminFullInterviewerReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['application_round', 'application_round__application']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Feedback.objects.all()
        
        # Get query parameters
        application_round_id = self.request.query_params.get('application_round')
        application_id = self.request.query_params.get('application')
        candidate_id = self.request.query_params.get('candidate')
        
        # Filter by appropriate parameters
        if application_round_id:
            queryset = queryset.filter(application_round_id=application_round_id)
        
        if application_id:
            queryset = queryset.filter(application_round__application_id=application_id)
            
        if candidate_id:
            queryset = queryset.filter(application_round__application__candidate_id=candidate_id)
        
        # Role-based access control
        if user.role == 'admin':
            # Admin can see all feedback
            return queryset
        elif user.role == 'interviewer':
            # Interviewers can only see feedback for rounds they conducted
            return queryset.filter(application_round__interviewer=user)
        elif user.role == 'candidate':
            # Candidates can only see feedback for their own applications
            return queryset.filter(application_round__application__candidate=user)
        
        return Feedback.objects.none()  # Default to empty queryset

# class CandidateFeedbackListView(generics.ListAPIView):
#     serializer_class = FeedbackSerializer

#     def get_queryset(self):
#         user = self.request.user

#         if user.role != 'candidate':
#             raise PermissionDenied("You are not authorized to view feedbacks.")
        
#         job_applications = JobApplication.objects.filter(candidate=user)
#         application_rounds = ApplicationRound.objects.filter(application__in=job_applications)

#         feedbacks = Feedback.objects.filter(application_round__in=application_rounds)
        
#         return feedbacks

class MyInterviewsView(generics.ListAPIView):
    serializer_class = ApplicationRoundSerializer
    permission_classes = [IsAuthenticated, IsInterviewer]

    def get_queryset(self):
        user = self.request.user
        
        if user.role != 'interviewer':
            return ApplicationRound.objects.none()
        
        return ApplicationRound.objects.filter(interviewer=user)

class UpcomingInterviewsView(generics.ListAPIView):
    serializer_class = ApplicationRoundSerializer
    permission_classes = [IsAuthenticated, IsAdminOrInterviewer]
    
    def get_queryset(self):
        from django.utils import timezone
        user = self.request.user
        
        if user.role == 'interviewer':
            # Interviewers can only see their own upcoming interviews
            return ApplicationRound.objects.filter(
                interviewer=user,
                scheduled_time__gt=timezone.now()
            ).order_by('scheduled_time')
        else:
            # Admins can see all upcoming interviews
            return ApplicationRound.objects.filter(
                scheduled_time__gt=timezone.now()
            ).order_by('scheduled_time')



