from django.urls import path
from . import views

app_name = 'authentication'
urlpatterns = [
    path('register',views.RegistrationView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>', views.ActivateAccountView.as_view(), name='activate'),
    path('reset-password/<uidb64>/<token>', views.PasswordResetView.as_view(), name='reset-password'),
    path('home', views.HomeView.as_view(), name='home'),
    path('request-reset-email', views.RequestResetEmailView.as_view(), name='request-reset-email'),
]
