from django.urls import path
# from account.api.views import registration_view
from account.api.views import UserCreateView,UserDetailView

urlpatterns = [
    # path('register/',registration_view,name='register'),
    path('register/',UserCreateView.as_view(),name='register'),
    path('users/<int:pk>/',UserDetailView.as_view(),name = 'user-detail')
]