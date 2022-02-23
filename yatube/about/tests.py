from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class StaticUrlsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exist_at_desired_location(self):
        """Cтраницы доступны любому пользователю."""
        urls_codes = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
            'unexpected_page/': HTTPStatus.NOT_FOUND,
        }
        for address, code in urls_codes.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)


class StaticUrlsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи namespace:name, доступен."""
        reverse_codes = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for reverse_name, code in reverse_codes.items():
            response = self.guest_client.get(reverse_name)
            self.assertEqual(response.status_code, code)

    def test_about_page_uses_correct_template(self):
        """При запросе к namespace:name
        применяются соответствующие шаблоны."""
        reverse_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in reverse_templates.items():
            response = self.guest_client.get(reverse_name)
            self.assertTemplateUsed(response, template)
