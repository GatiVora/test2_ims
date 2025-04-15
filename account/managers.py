from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self,email,password,**kwargs):
        if not email:
            raise ValueError("Email is requires")
        if not kwargs.get('first_name'):
            raise ValueError("First name is required")
        if not kwargs.get('last_name'):
            raise ValueError("Last name is required")
        if not password:
            raise ValueError("Password is required")

        user = self.model(
            email = self.normalize_email(email),
            **kwargs
        )

        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self,email,password,**kwargs):
        
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_staff", True)
        
        return self.create_user(email = email,password = password,**kwargs)

