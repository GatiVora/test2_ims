from django.db import migrations

# SQL for creating stored procedures
class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0001_initial'),  # Update this to your latest migration
    ]

    # This SQL creates a stored procedure for selecting a candidate
    select_candidate_procedure = """
    CREATE OR REPLACE PROCEDURE select_candidate(
        application_id INTEGER,
        selected_by VARCHAR(150)
    )
    LANGUAGE plpgsql
    AS $$
    DECLARE
        job_id INTEGER;
        candidate_id INTEGER;
        candidate_email VARCHAR(255);
        job_title VARCHAR(100);
    BEGIN
        -- Get information about the application
        SELECT 
            ja.job_id, 
            ja.candidate_id, 
            u.email, 
            j.title 
        INTO 
            job_id, 
            candidate_id, 
            candidate_email,
            job_title
        FROM 
            interview_jobapplication ja
            JOIN account_user u ON ja.candidate_id = u.id
            JOIN interview_job j ON ja.job_id = j.id
        WHERE 
            ja.id = application_id;

        -- Mark the candidate as selected
        UPDATE interview_jobapplication
        SET 
            is_selected = TRUE,
            status = 'closed',
            updated_at = NOW()
        WHERE 
            id = application_id;
            
        -- Close the job if needed (optional - uncomment if you want this behavior)
        -- UPDATE interview_job
        -- SET is_open = FALSE, updated_at = NOW()
        -- WHERE id = job_id;
        
        -- Close all other applications for this job
        UPDATE interview_jobapplication
        SET 
            status = 'closed',
            updated_at = NOW()
        WHERE 
            job_id = job_id 
            AND id != application_id 
            AND status != 'closed';
            
        -- Log the selection in a log table (you might need to create this table)
        -- You can uncomment and use this if you create a selection_log table
        /*
        INSERT INTO selection_log (
            application_id, 
            candidate_id,
            job_id,
            selected_by,
            selected_at
        ) VALUES (
            application_id,
            candidate_id,
            job_id,
            selected_by,
            NOW()
        );
        */
        
        RAISE NOTICE 'Candidate % selected for job %', candidate_id, job_title;
    END;
    $$;
    """
    
    # This SQL creates a stored procedure for tracking application status changes
    track_application_status_procedure = """
    CREATE OR REPLACE PROCEDURE track_application_status(
        application_id INTEGER,
        new_status VARCHAR(20),
        updated_by VARCHAR(150)
    )
    LANGUAGE plpgsql
    AS $$
    DECLARE
        old_status VARCHAR(20);
        candidate_name VARCHAR(255);
        job_title VARCHAR(100);
    BEGIN
        -- Get the current status and other info
        SELECT 
            ja.status,
            CONCAT(u.first_name, ' ', u.last_name),
            j.title
        INTO 
            old_status,
            candidate_name,
            job_title
        FROM 
            interview_jobapplication ja
            JOIN account_user u ON ja.candidate_id = u.id
            JOIN interview_job j ON ja.job_id = j.id
        WHERE 
            ja.id = application_id;
            
        -- Only update if status is different
        IF old_status != new_status THEN
            -- Update the application status
            UPDATE interview_jobapplication
            SET 
                status = new_status,
                updated_at = NOW()
            WHERE 
                id = application_id;
                
            -- Log the status change (you might need to create this table)
            -- You can uncomment and use this if you create a status_log table
            /*
            INSERT INTO status_log (
                application_id,
                old_status,
                new_status,
                changed_by,
                changed_at
            ) VALUES (
                application_id,
                old_status,
                new_status,
                updated_by,
                NOW()
            );
            */
            
            RAISE NOTICE 'Status for % application to % changed from % to %', 
                candidate_name, job_title, old_status, new_status;
        ELSE
            RAISE NOTICE 'Status already set to % for % application to %', 
                new_status, candidate_name, job_title;
        END IF;
    END;
    $$;
    """
    
    # This SQL creates a function to get application statistics
    application_statistics_function = """
    CREATE OR REPLACE FUNCTION get_application_statistics(
        job_id INTEGER DEFAULT NULL
    )
    RETURNS TABLE (
        job_title VARCHAR(100),
        total_applications BIGINT,
        new_applications BIGINT,
        in_progress_applications BIGINT,
        closed_applications BIGINT,
        selected_applications BIGINT,
        average_rating NUMERIC(3,1)
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT
            j.title as job_title,
            COUNT(ja.id) as total_applications,
            COUNT(ja.id) FILTER (WHERE ja.status = 'new') as new_applications,
            COUNT(ja.id) FILTER (WHERE ja.status = 'inprogress') as in_progress_applications,
            COUNT(ja.id) FILTER (WHERE ja.status = 'closed') as closed_applications,
            COUNT(ja.id) FILTER (WHERE ja.is_selected = TRUE) as selected_applications,
            COALESCE(AVG(f.rating), 0.0) as average_rating
        FROM
            interview_job j
            LEFT JOIN interview_jobapplication ja ON j.id = ja.job_id
            LEFT JOIN interview_applicationround ar ON ja.id = ar.application_id
            LEFT JOIN interview_feedback f ON ar.id = f.application_round_id
        WHERE
            (job_id IS NULL OR j.id = job_id)
        GROUP BY
            j.id, j.title
        ORDER BY
            j.title;
    END;
    $$;
    """

    operations = [
        migrations.RunSQL(select_candidate_procedure),
        migrations.RunSQL(track_application_status_procedure),
        migrations.RunSQL(application_statistics_function),
    ] 