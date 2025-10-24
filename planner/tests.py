from django.test import TestCase, Client
from django.urls import reverse, resolve
from .views import login_user, logout_user, register_user, login_user_ajax, logout_user_ajax, register_user_ajax

class AuthenticationURLSTest(TestCase):

    def test_login_url_resolves(self):
        """Test URL '/auth/login/' resolves ke view login_user."""
        url = reverse('authentication:login_user')
        # Memastikan URL '/auth/login/' me-resolve ke view 'login_user'
        self.assertEqual(resolve(url).func, login_user)

    def test_logout_url_resolves(self):
        """Test URL '/auth/logout/' resolves ke view logout_user."""
        url = reverse('authentication:logout_user')
        # Memastikan URL '/auth/logout/' me-resolve ke view 'logout_user'
        self.assertEqual(resolve(url).func, logout_user)

    def test_register_url_resolves(self):
        """Test URL '/auth/register/' resolves ke view register_user."""
        url = reverse('authentication:register_user')
        # Memastikan URL '/auth/register/' me-resolve ke view 'register_user'
        self.assertEqual(resolve(url).func, register_user)

    def test_login_api_url_resolves(self):
        """Test URL '/auth/api/login/' resolves ke view login_user_ajax."""
        url = reverse('authentication:login_api')
        # Memastikan URL '/auth/api/login/' me-resolve ke view 'login_user_ajax'
        self.assertEqual(resolve(url).func, login_user_ajax)

    def test_logout_api_url_resolves(self):
        """Test URL '/auth/api/logout/' resolves ke view logout_user_ajax."""
        url = reverse('authentication:logout_api')
         # Memastikan URL '/auth/api/logout/' me-resolve ke view 'logout_user_ajax'
        self.assertEqual(resolve(url).func, logout_user_ajax)

    def test_register_api_url_resolves(self):
        """Test URL '/auth/api/register/' resolves ke view register_user_ajax."""
        url = reverse('authentication:register_api')
        # Memastikan URL '/auth/api/register/' me-resolve ke view 'register_user_ajax'
        self.assertEqual(resolve(url).func, register_user_ajax)