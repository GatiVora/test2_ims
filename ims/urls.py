"""
URL configuration for ims project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [

    path('api/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('admin/', admin.site.urls),
    path('api/account/',include('account.api.urls')),
    path('api/',include('interview.api.urls')),

]

'''
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0NDY4NDQ3NSwiaWF0IjoxNzQ0NjEyNDc1LCJqdGkiOiI0YmU4ZWJmYzlhNmQ0MmVhOGQ0ZDViMTI1MWI4ZGZiOSIsInVzZXJfaWQiOjJ9.L-E9QK-132MgBojO_GQ0bUfltkrvHUm0E4l24_xmP5s",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0NjEyNzc1LCJpYXQiOjE3NDQ2MTI0NzUsImp0aSI6ImNiZjE2Y2Y3NjczZTQ4YjRiZGVmY2U3OGExNTMyMWEzIiwidXNlcl9pZCI6Mn0.yUmFPtIemALj0UsB7IGQxNNO2QlYiRRPYctj1k5v8F8"
}
'''