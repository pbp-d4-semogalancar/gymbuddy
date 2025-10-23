# community/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from http import HTTPStatus 
from .models import Thread
from .forms import ThreadForm

# ====================================================================
# A. TEST MODEL & FORMS
# ====================================================================

class ThreadModelAndFormTest(TestCase):
    """Menguji Model Thread dan Form ThreadForm."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.thread = Thread.objects.create(
            title='Judul Uji',
            content='Isi konten uji.',
            user=self.user
        )

    def test_model_fields(self):
        """Pastikan field model terisi dengan benar."""
        self.assertEqual(self.thread.title, 'Judul Uji')
        self.assertEqual(self.thread.content, 'Isi konten uji.')

    def test_threadform_validity(self):
        """Pastikan ThreadForm valid dengan data yang benar."""
        form = ThreadForm(data={'title': 'Form Test', 'content': 'Isi Form'})
        self.assertTrue(form.is_valid())

    def test_threadform_invalidity(self):
        """Pastikan ThreadForm tidak valid jika Judul kosong."""
        form = ThreadForm(data={'title': '', 'content': 'Isi Form'})
        self.assertFalse(form.is_valid())

# ====================================================================
# B. TEST VIEWS (CRUD User & AJAX)
# ====================================================================

class ThreadViewsTest(TestCase):
    """Menguji fungsionalitas Views Thread (READ, CREATE AJAX, UPDATE, DELETE)."""
    
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.other_user = User.objects.create_user(username='intruder', password='password456')
        
        self.thread = Thread.objects.create(
            title='Original Title',
            content='Original Content',
            user=self.owner
        )
        
        # URLs yang diuji
        self.community_url = reverse('community:show_community')
        self.create_ajax_url = reverse('community:create_thread_ajax')
        self.edit_url = reverse('community:edit_thread_user', args=[self.thread.id])
        self.delete_url = reverse('community:delete_thread_user', args=[self.thread.id])

    # --- READ (show_community) ---
    def test_show_community_get(self):
        """Pastikan halaman komunitas termuat dengan sukses."""
        response = self.client.get(self.community_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'community/community_page.html')

    # --- CREATE (create_thread_ajax) ---
    def test_create_thread_ajax_success(self):
        """Pengguna yang login harus bisa membuat thread via AJAX."""
        self.client.login(username='owner', password='password123')
        initial_count = Thread.objects.count()
        
        response = self.client.post(self.create_ajax_url, {
            'title': 'Ajax Test',
            'content': 'Isi dari Ajax test'
        })
        
        self.assertEqual(response.status_code, HTTPStatus.CREATED) # Status 201
        self.assertEqual(Thread.objects.count(), initial_count + 1)
        self.assertIn('success', response.json()['status'])
        
    def test_create_thread_ajax_requires_login(self):
        """Pastikan Create AJAX redirect ke URL login yang benar."""
        response = self.client.post(self.create_ajax_url, {'title': 'New', 'content': 'Test'}, follow=True)
        
        # FIX FINAL: Mengharuskan test mengharapkan URL custom Anda
        expected_login_path = reverse('community:login')
        expected_url = expected_login_path + '?next=' + self.create_ajax_url

        self.assertRedirects(response, expected_url) 
        
    # --- UPDATE (edit_thread_user) ---
    def test_edit_thread_user_success(self):
        """Pemilik thread harus bisa mengedit threadnya."""
        self.client.login(username='owner', password='password123')
        
        new_data = {'title': 'Updated Title', 'content': 'Updated Content'}
        response = self.client.post(self.edit_url, new_data)
        
        self.assertRedirects(response, self.community_url)
        self.thread.refresh_from_db()
        self.assertEqual(self.thread.title, 'Updated Title')
        
    def test_edit_thread_user_permission_denied(self):
        """User lain tidak boleh mengedit thread orang lain."""
        self.client.login(username='intruder', password='password456')
        
        new_data = {'title': 'Hacked Title', 'content': 'Hacked Content'}
        response = self.client.post(self.edit_url, new_data)
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN) # Status 403

    # --- DELETE (delete_thread_user) ---
    def test_delete_thread_user_success(self):
        """Pemilik thread harus bisa menghapus threadnya."""
        self.client.login(username='owner', password='password123')
        initial_count = Thread.objects.count()

        response = self.client.post(self.delete_url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Thread.objects.count(), initial_count - 1)
        self.assertIn('success', response.json()['status'])

    def test_delete_thread_user_permission_denied(self):
        """User lain tidak boleh menghapus thread orang lain."""
        self.client.login(username='intruder', password='password456')
        initial_count = Thread.objects.count()
        
        response = self.client.post(self.delete_url)
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN) # Status 403
        self.assertEqual(Thread.objects.count(), initial_count)