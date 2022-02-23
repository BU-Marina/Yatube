from http import HTTPStatus
from django.test import TestCase, Client
from posts.models import User


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='noname')

    def setUp(self):
        self.guest_client = Client()
        user = UserURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(user)

    def test_public_urls_exist_at_desired_location(self):
        """Общедоступные страницы доступны любому пользователю."""
        public_urls_codes = {
            '/auth/logout/': HTTPStatus.OK,
            '/auth/signup/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/password_reset/done/': HTTPStatus.OK,
            '/auth/reset/<uidb64>/<token>/': HTTPStatus.OK,
            '/auth/reset/done/': HTTPStatus.OK,
            'unexpected_page/': HTTPStatus.NOT_FOUND,
        }
        for address, code in public_urls_codes.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_private_urls_exist_at_desired_location(self):
        """Страницы для авторизованных пользователей доступны только
        авторизованному пользователю.
        """
        private_urls_codes = {
            '/auth/password_change/': HTTPStatus.OK,
            '/auth/password_change/done/': HTTPStatus.OK,
        }
        for address, code in private_urls_codes.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_private_urls_redirect_anonymous(self):
        """Страницы для авторизованных пользователей перенаправляют
        анонимного пользователя.
        """
        private_urls_away_adresses = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]
        for address in private_urls_away_adresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={address}')

    def test_urls_use_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            '/auth/logout/': 'users/logged_out.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            f'/auth/reset/{"Mw"}/{"5si-f7ab5e9f2a875e9b7c61"}/': (
                'users/password_reset_confirm.html'
            ),
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                try:
                    self.assertTemplateUsed(response, template)
                except AssertionError:
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)
