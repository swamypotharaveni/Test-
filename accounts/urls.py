from django.urls import path,include
from rest_framework.routers import DefaultRouter
from.views import UserViewSet
from.views import PasswordChange,ForgotPasswordOTP,ResetPasswordWithOTP,Profile
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # User CRUD routes
    path('', include(router.urls)),
    path("change_old_password",PasswordChange.as_view(),name="change_password"),
    path("forget_password/",ForgotPasswordOTP.as_view(),name="forget_password"),
    path("reset_password",ResetPasswordWithOTP.as_view(),name="reset_password"),
    path("Profile/",Profile.as_view(),name="profile"),
    
    
]