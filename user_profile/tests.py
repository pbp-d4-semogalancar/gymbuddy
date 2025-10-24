import json
from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from user_profile.forms import ProfileForm
from .models import Profile

class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="burhan", password="password123")

    def test_profile_creation_and_defaults(self):
        profile = Profile.objects.create(user=self.user, display_name="Burhan")
        profile.save()
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.display_name, "Burhan")
        self.assertEqual(profile.bio, "")
        self.assertEqual(list(profile.favorite_workouts), [])

    def test_str_method(self):
        profile = Profile.objects.create(user=self.user, display_name="Burhan")
        self.assertEqual(str(profile), "Burhan")

    def test_favorite_workouts_assignment(self):
        profile = Profile.objects.create(
            user=self.user,
            display_name="Burhan",
            favorite_workouts=['bench-press', 'running', 'yoga']
        )
        self.assertEqual(len(profile.favorite_workouts), 3)
        self.assertIn('bench-press', profile.favorite_workouts)
        self.assertIn('running', profile.favorite_workouts)
        self.assertIn('yoga', profile.favorite_workouts)

    def test_favorite_workouts_empty_or_full(self):
        profile_empty = Profile.objects.create(user=self.user, display_name="BurhanEmpty")
        self.assertEqual(list(profile_empty.favorite_workouts), [])

        all_choices = [choice[0] for choice in Profile.CATEGORY_CHOICES]
        profile_full = Profile.objects.create(user=User.objects.create_user("test2"), display_name="BurhanFull",
                                              favorite_workouts=all_choices)
        self.assertEqual(len(profile_full.favorite_workouts), len(all_choices))

    def test_one_to_one_constraint(self):
        Profile.objects.create(user=self.user, display_name="Burhan")
        with self.assertRaises(Exception):
            Profile.objects.create(user=self.user, display_name="Burhan2")

    def test_profile_picture_filename_format(self):
        profile = Profile(user=self.user, display_name="Burhan")
        profile.save()
        filename = profile.profile_picture.field.upload_to(profile, "mypic.png")
        self.assertTrue(filename.endswith('.png'))

    def test_long_display_name(self):
        long_name = "B" * 40
        profile = Profile.objects.create(user=User.objects.create_user("longuser"), display_name=long_name)
        self.assertEqual(profile.display_name, long_name)

    def test_empty_bio(self):
        profile = Profile.objects.create(user=User.objects.create_user("biotest"), display_name="BioTest")
        self.assertEqual(profile.bio, "")

    def test_update_favorite_workouts(self):
        profile = Profile.objects.create(user=User.objects.create_user("updatefw"), display_name="UpdateFW")
        profile.favorite_workouts = ['push-up', 'squat']
        profile.save()
        profile.refresh_from_db()
        self.assertEqual(len(profile.favorite_workouts), 2)
        self.assertIn('push-up', profile.favorite_workouts)
        self.assertIn('squat', profile.favorite_workouts)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="burhan", password="password123")
        self.user2 = User.objects.create_user(username="otheruser", password="pass456")
        self.profile = Profile.objects.create(user=self.user, display_name="Burhan")

    # ================= HTTP Views =================

    def test_create_profile_redirect_if_exists(self):
        self.client.login(username="burhan", password="password123")
        url = reverse('user_profile:create_profile')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('user_profile:detail_profile',
                                               args=[self.user.id, self.user.username]))

    def test_create_profile_page_get(self):
        self.client.login(username="otheruser", password="pass456")
        url = reverse('user_profile:create_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_user_profile.html')
        self.assertIsInstance(response.context['form'], ProfileForm)

    def test_edit_profile_redirect_if_no_profile(self):
        self.client.login(username="otheruser", password="pass456")
        url = reverse('user_profile:edit_profile')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('user_profile:create_profile'))

    def test_edit_profile_get(self):
        self.client.login(username="burhan", password="password123")
        url = reverse('user_profile:edit_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_user_profile.html')
        self.assertEqual(response.context['user_profile'], self.profile)

    def test_detail_profile_get(self):
        self.client.login(username="burhan", password="password123")
        url = reverse('user_profile:detail_profile', args=[self.user.id, self.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user_profile.html')
        self.assertEqual(response.context['user_profile'], self.profile)

    def test_delete_profile_permission(self):
        self.client.login(username="otheruser", password="pass456")
        url = reverse('user_profile:delete_profile', args=[self.user.id, self.user.username])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_delete_profile_success(self):
        self.client.login(username="burhan", password="password123")
        url = reverse('user_profile:delete_profile', args=[self.user.id, self.user.username])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('landing_page:landing_page'))
        self.assertFalse(Profile.objects.filter(user=self.user).exists())

    def test_show_json_by_id(self):
        url = reverse('user_profile:show_json_by_id', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['display_name'], self.profile.display_name)

    # ================= AJAX Views =================

    def test_create_profile_ajax_success(self):
        self.client.login(username="otheruser", password="pass456")
        url = reverse('user_profile:create_profile_ajax')
        response = self.client.post(url, {'display_name': 'NewUser', 'bio': 'Halo'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Profile.objects.filter(user=self.user2).exists())

    def test_create_profile_ajax_fail_existing(self):
        self.client.login(username="burhan", password="password123")
        url = reverse('user_profile:create_profile_ajax')
        response = self.client.post(url, {'display_name': 'Duplicate'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_edit_profile_ajax_success(self):
        self.client.login(username="burhan", password="password123")
        url = reverse('user_profile:edit_profile_ajax')
        data = {'display_name': 'Burhan Updated', 'bio': 'Bio baru'}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content['success'])
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.display_name, 'Burhan Updated')
        self.assertEqual(self.profile.bio, 'Bio baru')

    def test_edit_profile_ajax_fail_no_profile(self):
        self.client.login(username="otheruser", password="pass456")
        url = reverse('user_profile:edit_profile_ajax')
        response = self.client.post(url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content['success'])
        self.assertIn('Profil belum dibuat', content['message'])

class ProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="burhan", password="password123")

    def test_valid_form(self):
        data = {
            'display_name': 'Burhan',
            'bio': 'Ini bio saya',
            'favorite_workouts': ['bench-press', 'running']
        }
        # Simulasi upload file
        file_data = {
            'profile_picture': SimpleUploadedFile("test.png", b"file_content", content_type="image/png")
        }
        form = ProfileForm(data=data, files=file_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_empty_display_name(self):
        data = {
            'display_name': '',
            'bio': 'Ini bio saya'
        }
        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('display_name', form.errors)

    def test_bio_optional(self):
        data = {
            'display_name': 'Burhan',
            'bio': ''
        }
        form = ProfileForm(data=data)
        self.assertTrue(form.is_valid())

    def test_favorite_workouts_optional(self):
        data = {
            'display_name': 'Burhan',
            'bio': 'Bio saya'
        }
        form = ProfileForm(data=data)
        self.assertTrue(form.is_valid())

    def test_display_name_max_length(self):
        data = {
            'display_name': 'B' * 50,
            'bio': 'Bio saya'
        }
        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('display_name', form.errors)