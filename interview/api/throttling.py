from rest_framework.throttling import UserRateThrottle

class FeedbackRateThrottle(UserRateThrottle):
    """
    Throttle for feedback submission - limits how many feedback submissions 
    an interviewer can make in a day.
    """
    scope = 'interview_feedback'


class JobApplicationRateThrottle(UserRateThrottle):
    """
    Throttle for job applications - limits how many job applications 
    a candidate can submit in a day.
    """
    scope = 'job_application' 