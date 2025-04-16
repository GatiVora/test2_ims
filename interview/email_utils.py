# Import necessary libraries
import os  # For file path operations
import datetime  # For getting the current year
from jinja2 import Environment, FileSystemLoader, select_autoescape  # Jinja2 for templates
from django.core.mail import send_mail  # Django's email function
from django.conf import settings  # To access Django settings

# Step 1: Create a function to set up the Jinja2 environment
def get_jinja_environment():
    """
    This function sets up Jinja2 to find our templates.
    It's like telling Jinja2 where to look for template files.
    """
    # Find the full path to the templates directory
    # __file__ is the current file (email_utils.py)
    # os.path.dirname gets the directory containing this file
    # We then join this with 'templates' to get the full path
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    # Create a new Jinja2 environment
    env = Environment(
        # FileSystemLoader tells Jinja2 to load templates from the file system
        loader=FileSystemLoader(templates_dir),
        # autoescape helps secure the templates against XSS attacks
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Return the configured environment
    return env

# Step 2: Create a function to render the email using our template
def render_feedback_email(template_data, is_candidate=True):
    """
    This function fills our template with data.
    It's like filling in the blanks in a form letter.
    
    Args:
        template_data: A dictionary with all the data we want to show in the email
        is_candidate: A boolean indicating if we're sending to a candidate or admin
    
    Returns:
        A complete HTML email as a string
    """
    # Get the Jinja2 environment we set up in the previous function
    env = get_jinja_environment()
    
    # Get the specific template file we want to use
    template = env.get_template('emails/feedback_notification.html')
    
    # Add some common data that all emails need
    template_data.update({
        # Get company name from Django settings
        'company_name': settings.COMPANY_NAME,
        # Get current year for the copyright notice
        'current_year': datetime.datetime.now().year,
        # These flags control which parts of the template are shown
        'is_candidate': is_candidate,
        'is_admin': not is_candidate
    })
    
    # Fill in the template with our data and return the result
    return template.render(**template_data)

# Step 3: Create a function to send the email
def send_feedback_notification_email(recipient_email, subject, html_content):
    """
    This function sends the actual email using Django's email system.
    
    Args:
        recipient_email: The email address to send to
        subject: The email subject line
        html_content: The HTML content of the email (from our template)
    """
    # Use Django's send_mail function to send the email
    send_mail(
        # The subject line of the email
        subject=subject,
        
        # A plain text version for email clients that don't support HTML
        message="This email contains formatted content about interview feedback. "
               "Please use an email client that supports HTML to view it properly.",
        
        # Who the email appears to be from
        from_email=settings.DEFAULT_FROM_EMAIL,
        
        # Who to send the email to (as a list)
        recipient_list=[recipient_email],
        
        # The HTML version of the email (with all our styling)
        html_message=html_content,
        
        # Set to False so we can see any errors
        fail_silently=False,
    ) 