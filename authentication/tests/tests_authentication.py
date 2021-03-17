from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class BaseTest(TestCase):
    """BaseTest class sets up variables to be used in testing.
    All test classes will inherit from this class in order to get access to variables"""

    def setUp(self):
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')
        self.user = {
            'email': 'testuser@gmail.com',
            'username': 'username',
            'password': 'password',
            'password2': 'password',
            'name': 'firstname lastname',
        }
        self.user_short_password = {
            'email': 'testuser@gmail.com',
            'username': 'username',
            'password': 'pass',
            'password2': 'pass',
            'name': 'firstname lastname',
        }
        self.user_unmatching_password = {
            'email': 'testuser@gmail.com',
            'username': 'username',
            'password': 'password',
            'password2': 'password2',
            'name': 'firstname lastname',
        }
        self.user_invalid_email = {
            'email': 'testuser.com',
            'username': 'username',
            'password': 'password',
            'password2': 'password',
            'name': 'firstname lastname',
        }
        return super().setUp()

    
class RegisterTest(BaseTest):
    
    def test_can_view_page_correctly(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register.html')

    def test_can_register_user(self):
        response = self.client.post(self.register_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 302)
    
    def test_cant_register_user_short_password(self):
        response = self.client.post(self.register_url, self.user_short_password, format='text/html')
        self.assertEqual(response.status_code, 400)
    
    def test_cant_register_user_unmatching_password(self):
        response = self.client.post(self.register_url, self.user_unmatching_password, format='text/html')
        self.assertEqual(response.status_code, 400)
    
    def test_cant_register_user_invalid_email(self):
        response = self.client.post(self.register_url, self.user_invalid_email, format='text/html')
        self.assertEqual(response.status_code, 400)
    
    def test_cant_register_with_taken_email(self):
        self.client.post(self.register_url, self.user, format='text/html')
        response = self.client.post(self.register_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 400)


class LoginTest(BaseTest):
    
    def test_can_access_page(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_login_sucess(self):
        self.client.post(self.register_url, self.user, format='text/html')
        user = User.objects.filter(email=self.user['email']).first()
        user.is_active = True
        user.save()
        response = self.client.post(self.login_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 302)

    def test_cant_login(self):
        self.client.post(self.register_url, self.user, format='text/html')
        response = self.client.post(self.login_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 401)

