from django.urls import path
from django.views.generic import TemplateView
from .views import RoleRequestCreateView, UserRegisterView, UserLoginView, UserLogoutView, UserProfileView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('request-role/', RoleRequestCreateView.as_view(), name='request_role'),
    path('request-role/success/', TemplateView.as_view(template_name='users/role_request_success.html'), name='role_request_success'),
]