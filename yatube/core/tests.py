from http import HTTPStatus
from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        '''При запросе неизвестной страницы сервер возвращает код ошибки 404
        и используется кастомный шаблон
        '''
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
