from django.urls import path

from .views import (
    RegisterCompanyView, 
    RegisterUserView,
    UserLoginView,
    UserProfileView,
    UserLogoutView,
    ProfileDeleteView
)


urlpatterns = [
    path('register/company/', RegisterCompanyView.as_view(), name='register'),
    path('register/user/', RegisterUserView.as_view(), name='register_user'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/delete/', ProfileDeleteView.as_view(), name='profile_delete'),
]