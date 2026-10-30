from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthenticationFlowTests(TestCase):
    def test_register_page_renders(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tạo tài khoản')

    def test_user_can_register_and_is_logged_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'khanh_test',
            'email': 'khanh.test@example.com',
            'password1': 'A-strong-test-password-2026',
            'password2': 'A-strong-test-password-2026',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='khanh_test').exists())
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username='existing_user',
            email='same@example.com',
            password='Existing-password-2026',
        )
        response = self.client.post(reverse('register'), {
            'username': 'new_user',
            'email': 'SAME@example.com',
            'password1': 'A-strong-test-password-2026',
            'password2': 'A-strong-test-password-2026',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='new_user').exists())

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Đăng nhập')
