# Import necessary libraries
from celery import shared_task  # For creating background tasks
from django.core.mail import send_mail  # For sending emails
from django.conf import settings  # To access Django settings
from django.utils import timezone  # For working with dates and times
from django.db import models  # For database operations
from datetime import datetime, timedelta  # For date calculations
from interview.email_utils import render_feedback_email, send_feedback_notification_email  # Our own email functions

@shared_task
def send_feedback_notification(feedback_id):
    """
    This task sends email notifications when feedback is submitted.
    It runs in the background, so the user doesn't have to wait for emails to send.
    
    Args:
        feedback_id: The ID of the feedback in the database
    """
    from interview.models import Feedback
    from account.models import User
    
    try:
        # Step 1: Get the feedback data from the database
        # We use select_related to efficiently get all related data in one query
        feedback = Feedback.objects.select_related(
            'application_round__application__candidate',
            'application_round__interviewer',
            'application_round__application__job'
        ).get(id=feedback_id)
        
        # Step 2: Extract the data we need for the emails
        candidate = feedback.application_round.application.candidate
        interviewer = feedback.application_round.interviewer
        job = feedback.application_round.application.job
        feedback_date = timezone.now().strftime('%Y-%m-%d %H:%M')
        
        # Step 3: Prepare the email for the candidate
        candidate_subject = f"New feedback for your {job.title} application"
        
        # This dictionary contains all the data we want to show in the candidate's email
        candidate_template_data = {
            'subject': candidate_subject,
            'recipient_name': candidate.first_name,
            'job_title': job.title,
            'interviewer_name': f"{interviewer.first_name} {interviewer.last_name}",
            'feedback_date': feedback_date,
            'show_rating': False  # We don't show the rating to candidates
        }
        
        # Step 4: Render and send the candidate's email
        # First, we fill in the template with our data
        candidate_html = render_feedback_email(candidate_template_data, is_candidate=True)
        # Then we send the email
        send_feedback_notification_email(candidate.email, candidate_subject, candidate_html)
        
        # Step 5: Prepare and send emails to all admins
        # First, get a list of all admin email addresses
        admin_emails = list(
            User.objects.filter(role='admin').values_list('email', flat=True)
        )
        
        # If we found any admins, send them emails too
        if admin_emails:
            admin_subject = f"New feedback from {interviewer.first_name} for {candidate.first_name}"
            
            # This dictionary contains all the data for the admin emails
            admin_template_data = {
                'subject': admin_subject,
                'recipient_name': "Admin",
                'candidate_name': f"{candidate.first_name} {candidate.last_name}",
                'job_title': job.title,
                'interviewer_name': f"{interviewer.first_name} {interviewer.last_name}",
                'rating': feedback.rating,
                'feedback_date': feedback_date,
                'comments': feedback.comments
            }
            
            # Send an email to each admin
            for admin_email in admin_emails:
                # Render the template for this admin
                admin_html = render_feedback_email(admin_template_data, is_candidate=False)
                # Send the email
                send_feedback_notification_email(admin_email, admin_subject, admin_html)
        
        # Return a success message
        return f"Notification sent for feedback {feedback_id}"
    
    # Handle cases where the feedback doesn't exist
    except Feedback.DoesNotExist:
        return f"Feedback with ID {feedback_id} not found"
    # Handle any other errors
    except Exception as e:
        return f"Error sending notification: {str(e)}"

@shared_task
def send_interview_reminders():
    """
    This task sends reminder emails to interviewers about upcoming interviews.
    It runs automatically once per day through Celery Beat.
    """
    from interview.models import ApplicationRound
    
    # Step 1: Calculate the time window for reminders
    now = timezone.now()  # Current time
    next_24_hours = now + timedelta(hours=24)  # 24 hours from now
    
    # Step 2: Find all interviews scheduled in the next 24 hours
    upcoming_interviews = ApplicationRound.objects.filter(
        scheduled_time__gt=now,  # Greater than current time
        scheduled_time__lte=next_24_hours  # Less than or equal to 24 hours from now
    ).select_related(
        'interviewer',
        'application__candidate',
        'application__job'
    )
    
    # Step 3: Group interviews by interviewer
    # This way, each interviewer gets one email with all their interviews
    interviewer_interviews = {}
    for interview in upcoming_interviews:
        interviewer = interview.interviewer
        # If this is the first interview for this interviewer, create an entry
        if interviewer.id not in interviewer_interviews:
            interviewer_interviews[interviewer.id] = {
                'interviewer': interviewer,
                'interviews': []
            }
        # Add this interview to the interviewer's list
        interviewer_interviews[interviewer.id]['interviews'].append(interview)
    
    # Step 4: Send reminder emails to each interviewer
    for interviewer_data in interviewer_interviews.values():
        interviewer = interviewer_data['interviewer']
        interviews = interviewer_data['interviews']
        
        # Prepare the email subject
        subject = f"Reminder: You have {len(interviews)} interview(s) scheduled in the next 24 hours"
        
        # Start building the email message
        message = f"""
        Hello {interviewer.first_name},
        
        This is a reminder that you have the following interview(s) scheduled in the next 24 hours:
        
        """
        
        # Add details for each interview
        for interview in interviews:
            candidate = interview.application.candidate
            job = interview.application.job
            interview_time = interview.scheduled_time
            formatted_time = interview_time.strftime('%Y-%m-%d %H:%M')
            
            # Add this interview to the message
            message += f"""
        * {formatted_time} - {job.title}
          Candidate: {candidate.first_name} {candidate.last_name}
          Email: {candidate.email}
          Phone: {candidate.phone}
            """
        
        # Finish the message
        message += f"""
        
        Please be prepared and on time for your interviews.
        
        Best regards,
        {settings.COMPANY_NAME} Team
        """
        
        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[interviewer.email],
            fail_silently=False,
        )
    
    # Return a summary of what we did
    return f"Sent interview reminders to {len(interviewer_interviews)} interviewers" 