# Interview_Management_System



've implemented a scheduled task that sends interview reminders to interviewers. Here's what it does:
Task Function: send_interview_reminders in interview/tasks.py
This task is scheduled to run once per day
It finds all interviews scheduled in the next 24 hours
It groups interviews by interviewer so each interviewer gets one consolidated email
For each interviewer, it sends a reminder email listing all their upcoming interviews
Email Content:
Lists all interviews the interviewer has in the next 24 hours
Includes important details like:
Interview time
Job position
Candidate name
Candidate contact details (email and phone)
Scheduling:
The task is configured to run once daily in the CELERY_BEAT_SCHEDULE setting
To use this scheduled task, you'll need to run:
Apply to README.md

# Start Redis (if not already running)
redis-server

# Start Celery worker
celery -A ims worker -l info

# Start Celery beat for scheduled tasks
celery -A ims beat -l info




Great! I've implemented a comprehensive throttling system for your Interview Management System API. Here's what I've added:
Global Throttling Settings:
Added default throttling classes to your REST_FRAMEWORK settings
Set rate limits for both anonymous users (20 requests/hour) and authenticated users (100 requests/hour)
Added specific rate limits for feedback submissions (30/day) and job applications (10/day)
Custom Throttle Classes:
Created FeedbackRateThrottle for limiting feedback submissions
Created JobApplicationRateThrottle for limiting job applications
Applied Throttling to Views:
Added throttling to FeedbackCreateView to limit feedback submissions
Added throttling to JobApplicationListView with conditional throttling based on request method
Custom Exception Handler:
Implemented a custom exception handler that provides user-friendly error messages
Added specific messages for different throttle types
Shows wait time before the next request is allowed
This throttling system:
Prevents abuse of your API by limiting the number of requests
Provides different limits for different user types (anonymous vs. authenticated)
Adds stricter limits on resource-intensive operations (feedback submission, job applications)
Shows user-friendly error messages when limits are exceeded
The throttling is particularly useful for:
Preventing candidates from spamming applications
Limiting the API usage by anonymous users (potential abuse)
Ensuring fair usage of resources by all users
Protecting your server from overload
This implementation combines well with your Celery tasks, as throttling helps manage the number of tasks that get triggered by user actions.