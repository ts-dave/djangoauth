from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.decorators import method_decorator
from django.core.mail import EmailMessage
from django.conf import settings
from validate_email import validate_email
from .utils import generate_token

from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Create your views here.


class RegistrationView(View):

    def get(self, request):
        return render(request, 'auth/register.html')

    def post(self, request):
        context = {
            'has_error': False,
        }
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password2')
        username = request.POST.get('username')
        fullname = request.POST.get('name')

        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'Please provide a valid email')
            context['has_error'] = True

        if len(password1) < 6:
            messages.add_message(request, messages.ERROR,
                                 'Password should be more than 6 characters')
            context['has_error'] = True

        if password1 != password2:
            messages.add_message(request, messages.ERROR,
                                 'Passwords do not match')
            context['has_error'] = True

        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR, 'Email is taken')
            context['has_error'] = True

        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.ERROR, 'Username is taken')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'auth/register.html', context, status=400)

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password1)
        user.first_name = fullname.split()[0]
        user.last_name = fullname.split()[-1]
        user.is_active = False
        user.save()

        current_site = get_current_site(request)
        email_subject = 'Activate your Account'
        message = render_to_string('auth/activate.html', context={
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        })

        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
        )
        email_message.send()

        messages.add_message(request, messages.SUCCESS,
                             'Account created, activation email sent')
        return redirect('authentication:login')


class LoginView(View):

    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if not user:
            messages.add_message(request, messages.ERROR,
                                 'Username or Password is incorrect')
            return render(request, 'auth/login.html', status=401)

        login(request, user)
        return redirect('authentication:home')


class ActivateAccountView(View):

    def get(self, request, uidb64, token):

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

        except Exception:
            user = None

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Account activated successfully')
            return redirect('authentication:login')

        return render(request, 'auth/activate_failed.html', status=401)


class HomeView(LoginRequiredMixin, View):

    # @method_decorator(allowed_role = [])
    def get(self, request):
        return render(request, 'auth/home.html')


class LogoutView(LoginRequiredMixin, View):

    def post(self, request):
        logout(request)
        return redirect('authentication:login')


class RequestResetEmailView(View):

    def get(self, request):
        return render(request, 'auth/request-reset-email.html')

    def post(self, request):
        email = request.POST.get('email')

        if not validate_email(email):
            messages.ERROR(request, 'Please Enter Valid Email')
            return render(request, 'auth/request-reset-email.html')

        user = User.objects.filter(email=email)

        if user.exists():
            user = user[0]
            current_site = get_current_site(request)
            email_subject = 'Reset Your Password'
            message = render_to_string('auth/passwordreset.html', context={
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': PasswordResetTokenGenerator.make_token(user) # TODO: FIX BUG
            })

            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
            )
            email_message.send()

        messages.SUCCESS(
            request, 'You have been sent an email on how to reset password')
        return render(request, 'auth/request-reset-email.html')


class PasswordResetView(View):

    def get(self, request, uidb64, token):
        return render(request, 'auth/request-reset-email.html')

    def post(self, request):
        return render(request, 'auth/request-reset-email.html')
