from django.test import TestCase
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class TestAjaxAuthViews(TestCase):
    
    def setUp(self):
        """Siapkan environment tes"""
        self.client = Client()
        
        self.register_url = reverse('authentication:register_api')
        self.login_url = reverse('authentication:login_api')
        self.logout_url = reverse('authentication:logout_api')

        self.test_user_creds = {
            'username': 'testuser_ajax',
            'password': 'testpassword123'
        }
        self.user = User.objects.create_user(**self.test_user_creds)

    def test_register_user_ajax_success(self):
        """Test registrasi AJAX sukses"""
        data = {
            'username': 'ajaxuser',
            'password1': 'ajaxpass123',
            'password2': 'ajaxpass123'
        }
        response = self.client.post(
            self.register_url, 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='ajaxuser').exists())
        
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['username'], 'ajaxuser')

    def test_register_user_ajax_password_mismatch(self):
        """Test registrasi AJAX gagal karena password tidak cocok"""
        data = {
            'username': 'ajaxuser2',
            'password1': 'ajaxpass123',
            'password2': 'WRONG'
        }
        response = self.client.post(
            self.register_url, 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username='ajaxuser2').exists())
        self.assertEqual(response.json()['message'], 'Passwords do not match.')

    def test_register_user_ajax_username_exists(self):
        """Test registrasi AJAX gagal karena username sudah ada"""
        data = {
            'username': 'testuser_ajax',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        response = self.client.post(
            self.register_url, 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Username already exists.')
        
    def test_register_user_ajax_empty_field(self):
        """Test registrasi AJAX gagal karena field kosong"""
        data = {'username': '', 'password1': '123', 'password2': '123'}
        response = self.client.post(
            self.register_url, 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Username and password cannot be empty.')

    def test_login_user_ajax_success(self):
        """Test login AJAX sukses"""
        response = self.client.post(self.login_url, self.test_user_creds)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue('_auth_user_id' in self.client.session)
        self.assertEqual(response.json()['status'], True)
        self.assertEqual(response.json()['username'], self.test_user_creds['username'])

    def test_login_user_ajax_fail(self):
        """Test login AJAX gagal karena password salah"""
        data = {'username': self.test_user_creds['username'], 'password': 'WRONG'}
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, 401)
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertEqual(response.json()['status'], False)
        self.assertIn('periksa kembali', response.json()['message'])

    def test_logout_user_ajax_success(self):
        """Test logout AJAX sukses"""
        self.client.post(self.login_url, self.test_user_creds)
        self.assertTrue('_auth_user_id' in self.client.session)
        
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertEqual(response.json()['status'], True)
        self.assertEqual(response.json()['username'], self.test_user_creds['username'])