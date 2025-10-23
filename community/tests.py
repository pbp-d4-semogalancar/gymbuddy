import json
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from .models import Thread, Reply
from .forms import ReplyForm
from .views import (
    community_page_view, thread_detail_view, create_thread_ajax, add_reply_ajax,
    edit_thread_user, delete_thread_user, edit_reply_ajax, delete_reply_ajax,
)
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from http import HTTPStatus 
from .models import Thread
from .forms import ThreadForm

def create_test_user(username="testuser", password="password"):
    return User.objects.create_user(username=username, password=password)

class CommunityAppTests(TestCase):

    def setUp(self):
        self.user1 = create_test_user(username="user1")
        self.user2 = create_test_user(username="user2")
        self.client = Client()
        self.thread1 = Thread.objects.create(user=self.user1, title="Thread 1 Title", content="Thread 1 Content")
        self.reply1 = Reply.objects.create(user=self.user2, thread=self.thread1, content="Reply 1 Content")
        self.reply2 = Reply.objects.create(user=self.user1, thread=self.thread1, content="Reply 2 Content", parent=self.reply1) # Nested reply

    def test_reply_creation(self):
        self.assertEqual(self.reply1.content, "Reply 1 Content")
        self.assertEqual(self.reply1.user.username, "user2")
        self.assertEqual(self.reply1.thread, self.thread1)
        self.assertEqual(str(self.reply1), 'Reply by user2')
        self.assertIsNone(self.reply1.parent) # Top-level reply

    def test_nested_reply_creation(self):
        self.assertEqual(self.reply2.parent, self.reply1)
        self.assertEqual(self.reply1.children.count(), 1)
        self.assertIn(self.reply2, self.reply1.children.all())

    def test_reply_form_valid(self):
        form = ReplyForm(data={'content': 'Valid Reply Content'})
        self.assertTrue(form.is_valid())

    def test_reply_form_invalid(self):
        form = ReplyForm(data={'content': ''}) # Empty content
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_url_resolutions(self):
        self.assertEqual(resolve(reverse('community:thread_detail', args=[self.thread1.id])).func, thread_detail_view)
        self.assertEqual(resolve(reverse('community:add_reply_ajax', args=[self.thread1.id])).func, add_reply_ajax)
        self.assertEqual(resolve(reverse('community:edit_reply', args=[self.reply1.id])).func, edit_reply_ajax)
        self.assertEqual(resolve(reverse('community:delete_reply', args=[self.reply1.id])).func, delete_reply_ajax)

    def test_add_reply_ajax_unauthenticated(self):
        response = self.client.post(reverse('community:add_reply_ajax', args=[self.thread1.id]), json.dumps({'content': 'C'}), content_type='application/json')
        self.assertEqual(response.status_code, 302) # Should redirect to login

    def test_add_reply_ajax_authenticated(self):
        self.client.login(username="user1", password="password")
        response = self.client.post(reverse('community:add_reply_ajax', args=[self.thread1.id]), json.dumps({'content': 'New Reply'}), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'success')
        self.assertTrue(Reply.objects.filter(content="New Reply", thread=self.thread1, parent__isnull=True).exists())
        self.assertIn('New Reply', json_response['html_reply'])

    def test_add_nested_reply_ajax_authenticated(self):
        self.client.login(username="user1", password="password")
        response = self.client.post(reverse('community:add_reply_ajax', args=[self.thread1.id]), json.dumps({'content': 'Nested Reply', 'parent_id': self.reply1.id}), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'success')
        self.assertTrue(Reply.objects.filter(content="Nested Reply", thread=self.thread1, parent=self.reply1).exists())
        self.assertEqual(json_response['parent_id'], self.reply1.id)
        self.assertIn('Nested Reply', json_response['html_reply'])

    def test_edit_reply_ajax_user(self):
        self.client.login(username="user2", password="password") # user2 is the user of reply1
        response = self.client.post(reverse('community:edit_reply', args=[self.reply1.id]), json.dumps({'content': 'Updated Reply Content'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'success')
        self.reply1.refresh_from_db()
        self.assertEqual(self.reply1.content, 'Updated Reply Content')

    def test_edit_reply_ajax_not_user(self):
        self.client.login(username="user1", password="password") # user1 is not the user of reply1
        response = self.client.post(reverse('community:edit_reply', args=[self.reply1.id]), json.dumps({'content': 'Updated Reply Content'}), content_type='application/json')
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_delete_reply_ajax_user(self):
        self.client.login(username="user2", password="password") # user2 is user of reply1
        reply_id_to_delete = self.reply1.id
        response = self.client.post(reverse('community:delete_reply', args=[reply_id_to_delete]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertFalse(Reply.objects.filter(id=reply_id_to_delete).exists())

    def test_delete_reply_ajax_not_user(self):
        self.client.login(username="user1", password="password")
        response = self.client.post(reverse('community:delete_reply', args=[self.reply1.id]))
        self.assertEqual(response.status_code, 403)

# ====================================================================
# A. TEST MODEL & FORMS
# ====================================================================

class ThreadModelAndFormTest(TestCase):
    """Menguji Model Thread dan Form ThreadForm."""
    
    def setUp(self):
        # User dummy
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
        # ThreadForm hanya membutuhkan title dan content
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
        # User pemilik thread (untuk otorisasi)
        self.owner = User.objects.create_user(username='owner', password='password123')
        # User lain (untuk menguji penolakan otorisasi)
        self.other_user = User.objects.create_user(username='intruder', password='password456')
        
        self.thread = Thread.objects.create(
            title='Original Title',
            content='Original Content',
            user=self.owner
        )
        
        # URLs yang diuji (menggunakan nama URL dari community/urls.py)
        self.community_url = reverse('community:community_page')
        self.create_ajax_url = reverse('community:create_thread_ajax')
        self.edit_url = reverse('community:edit_thread_user', args=[self.thread.id])
        self.delete_url = reverse('community:delete_thread_user', args=[self.thread.id])

    # --- READ (community_page) ---
    def test_community_page_get(self):
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
        
        # FIX: Mengubah ekspektasi agar sesuai dengan output sistem: /accounts/login/
        # Karena settings.LOGIN_URL adalah '/accounts/login/', kita gunakan path string ini.
        expected_login_path = '/accounts/login/'
        expected_url = expected_login_path + '?next=' + self.create_ajax_url

        self.assertRedirects(response, expected_url)

    # --- UPDATE (edit_thread_user) ---
    def test_edit_thread_user_success(self):
        """Pemilik thread harus bisa mengedit threadnya."""
        self.client.login(username='owner', password='password123')
        
        new_data = {'title': 'Updated Title', 'content': 'Updated Content'}
        response = self.client.post(self.edit_url, new_data)
        
        # Test mengharapkan redirect ke halaman komunitas setelah sukses
        self.assertRedirects(response, self.community_url) 
        self.thread.refresh_from_db()
        self.assertEqual(self.thread.title, 'Updated Title')
        
    def test_edit_thread_user_permission_denied(self):
        """User lain tidak boleh mengedit thread orang lain."""
        self.client.login(username='intruder', password='password456')
        
        new_data = {'title': 'Hacked Title', 'content': 'Hacked Content'}
        response = self.client.post(self.edit_url, new_data)
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN) # Views mengembalikan 403

    # --- DELETE (delete_thread_user) ---
    def test_delete_thread_user_success(self):
        """Pemilik thread harus bisa menghapus threadnya."""
        self.client.login(username='owner', password='password123')
        initial_count = Thread.objects.count()

        response = self.client.post(self.delete_url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK) # Views mengembalikan 200 OK
        self.assertEqual(Thread.objects.count(), initial_count - 1)
        self.assertIn('success', response.json()['status'])

    def test_delete_thread_user_permission_denied(self):
        """User lain tidak boleh menghapus thread orang lain."""
        self.client.login(username='intruder', password='password456')
        initial_count = Thread.objects.count()
        
        response = self.client.post(self.delete_url)
        
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN) # Views mengembalikan 403
        self.assertEqual(Thread.objects.count(), initial_count)
