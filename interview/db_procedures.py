from django.db import connection


def select_candidate(application_id, selected_by):
    """
    Call the PostgreSQL stored procedure to select a candidate for a job.
    
    This procedure:
    1. Marks the application as selected
    2. Sets the application status to 'closed'
    3. Closes all other applications for the same job
    
    Args:
        application_id: The ID of the JobApplication to select
        selected_by: Username or identifier of the person making the selection
        
    Returns:
        True if successful
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "CALL select_candidate(%s, %s)",
            [application_id, selected_by]
        )
    return True


def update_application_status(application_id, new_status, updated_by):
    """
    Call the PostgreSQL stored procedure to update a job application's status.
    
    This procedure:
    1. Gets the current status
    2. Updates to the new status if different
    3. Records the change
    
    Args:
        application_id: The ID of the JobApplication to update
        new_status: The new status ('new', 'inprogress', or 'closed')
        updated_by: Username or identifier of the person making the change
        
    Returns:
        True if successful
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "CALL track_application_status(%s, %s, %s)",
            [application_id, new_status, updated_by]
        )
    return True


def get_application_statistics(job_id=None):
    """
    Call the PostgreSQL function to get statistics about job applications.
    
    Args:
        job_id: Optional job ID to filter by a specific job
        
    Returns:
        A list of dictionaries containing statistics for each job
    """
    with connection.cursor() as cursor:
        if job_id:
            cursor.execute("SELECT * FROM get_application_statistics(%s)", [job_id])
        else:
            cursor.execute("SELECT * FROM get_application_statistics()")
            
        columns = [col[0] for col in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
            
    return results 