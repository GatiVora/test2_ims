from django.db import models
from account.models import TimeStampModel
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

User = get_user_model()

class Job(TimeStampModel):

    POSITION_CHOICES = (
        ('software_engineer', 'Software Engineer'),
        ('senior_software_engineer', 'Senior Software Engineer'),
        ('tech_lead', 'Tech Lead'),
        ('manager', 'Manager'),
        ('intern', 'Intern'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    department = models.CharField(max_length=50)
    position = models.CharField(max_length=30, choices=POSITION_CHOICES)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.get_position_display()}"
    

class JobApplication(TimeStampModel):

    STATUS_CHOICES = (
        ('new', 'New'),
        ('inprogress', 'Inprogress'),
        ('closed', 'Closed'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User,on_delete=models.CASCADE,limit_choices_to={'role':'candidate'})
    applied_on = models.DateTimeField(auto_now_add=True)
    # resume = models.FileField(upload_to='resumes/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.candidate.fullname} applied to {self.job.title}"
    
class InterviewRound(TimeStampModel):
    TYPE_CHOICES = (
        ('aptitude', 'Aptitude'),
        ('technical', 'Technical'),
        ('coding', 'Coding Test'),
        ('hr', 'HR Interview'),
    )
    round_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='aptitude')
    job_application = models.ManyToManyField(JobApplication, through='ApplicationRound', related_name='interview_rounds')

class ApplicationRound(TimeStampModel):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='rounds')
    round = models.ForeignKey(InterviewRound, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    interviewer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'interviewer'})
    duration = models.IntegerField()

    def __str__(self):
        return f"{self.round.round_type} | {self.application.candidate.fullname}"

class Feedback(TimeStampModel):
    application_round = models.ForeignKey(ApplicationRound, on_delete=models.CASCADE, related_name='feedbacks')
    comments = models.TextField()
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])


