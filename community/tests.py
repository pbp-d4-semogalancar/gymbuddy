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
