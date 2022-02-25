from http import HTTPStatus
from django.core.cache import cache
from django.test import TestCase, Client
from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user_author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.author = PostURLTests.user_author
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.author)
        self.post_id = PostURLTests.post.pk
        cache.clear()

    def test_public_urls_exist_at_desired_location(self):
        """Общедоступные страницы доступны любому пользователю."""
        public_urls_codes = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.author.username}/': HTTPStatus.OK,
            f'/posts/{self.post_id}/': HTTPStatus.OK,
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
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post_id}/edit/': HTTPStatus.OK,
            '/follow/': HTTPStatus.OK,
        }
        for address, code in private_urls_codes.items():
            with self.subTest(address=address):
                response = self.authorized_author_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_private_urls_redirect_anonymous(self):
        """Страницы для авторизованных пользователей перенаправляют
        анонимного пользователя.
        """
        private_urls_away_adresses = [
            '/create/',
            f'/posts/{self.post_id}/edit/',
            '/follow/',
            f'/profile/{self.author.username}/follow/',
            f'/profile/{self.author.username}/unfollow/',
        ]
        for address in private_urls_away_adresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={address}')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author.username}/': 'posts/profile.html',
            f'/posts/{self.post_id}/': 'posts/post_detail.html',
            f'/posts/{self.post_id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/index.html',
            'unexpected_page/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author_client.get(address)
                self.assertTemplateUsed(response, template)
