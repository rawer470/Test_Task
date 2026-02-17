import json

from django.contrib.auth.models import User
from django.test import TestCase, Client


class RegisterTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_success(self):
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({'username': 'newuser', 'password': 'testpass123'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['username'], 'newuser')
        self.assertEqual(len(data['token']), 256)

    def test_register_duplicate_username(self):
        User.objects.create_user(username='existing', password='pass')
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({'username': 'existing', 'password': 'testpass123'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('already exists', response.json()['detail'])


class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_success(self):
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'testuser', 'password': 'testpass123'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['username'], 'testuser')
        self.assertIn('token', data)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'testuser', 'password': 'wrongpass'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)


class LogoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'testuser', 'password': 'testpass123'}),
            content_type='application/json',
        )
        self.token = response.json()['token']

    def test_logout_success(self):
        response = self.client.post(
            '/api/auth/logout',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )
        self.assertEqual(response.status_code, 200)

    def test_logout_without_token(self):
        response = self.client.post('/api/auth/logout')
        self.assertEqual(response.status_code, 401)
