from django.urls import path
from interview.api.views import (JobListCreateView,JobDetailView,JobApplicationsListView,OpenJobsListView,JobApplicationListView,
                                 JobApplicationDetailView,SelectCandidateView,MyApplicationsListView,InterviewRoundListView,
                                 ApplicationRoundListView,FeedbackCreateView,FeedbackListView,ApplicationStatisticsView)

urlpatterns = [
    path('job/',JobListCreateView.as_view(),name='job-list-create'),
    path('job/<int:pk>/',JobDetailView.as_view(),name='job-detail'),
    path('job/<int:pk>/applications/',JobApplicationsListView.as_view(),name='job-applications'),
    path('job/open/',OpenJobsListView.as_view(),name='open-jobs'),

    path('applications/',JobApplicationsListView.as_view(),name='applications-list'),
    path('applications/<int:pk>',JobApplicationDetailView.as_view(),name='application-detail'),
    path('applications/<int:pk>/select/',SelectCandidateView.as_view(),name='select-candidate'),
    path('my-applications/',MyApplicationsListView.as_view(),name='my-applications'),
    path('applications/statistics/',ApplicationStatisticsView.as_view(),name='application-statistics'),

    path('interview-rounds/',InterviewRoundListView.as_view(),name='rounds-list'),

    path('applications/<int:pk>/round/',ApplicationRoundListView.as_view(),name='application-round-detail'),
    path('application-round/<int:pk>/feedback/',FeedbackCreateView.as_view(),name='create-feedback'),
    path('feedback/',FeedbackListView.as_view(),name='feedback-list'),
    

]