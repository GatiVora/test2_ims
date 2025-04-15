from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission class to check if the user is an admin.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsInterviewer(permissions.BasePermission):
    """
    Permission class to check if the user is an interviewer.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'interviewer'

class IsCandidate(permissions.BasePermission):
    """
    Permission class to check if the user is a candidate.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'candidate'

class IsAdminOrInterviewer(permissions.BasePermission):
    """
    Permission class to check if the user is either an admin or an interviewer.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'interviewer'] 

class AdminFullInterviewerReadOnly(permissions.BasePermission):
    """
    Grants full access to admin, but read-only to interviewers.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admin has full access
        if request.user.role == 'admin':
            return True
            
        # Interviewer has read-only access
        if request.user.role == 'interviewer' and request.method in permissions.SAFE_METHODS:
            return True
            
        return False 