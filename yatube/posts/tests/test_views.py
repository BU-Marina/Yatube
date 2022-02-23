from django.core.cache import cache
from django import forms
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Follow, Post, Group, User
from ..forms import PostForm
from ..views import POSTS_AMOUNT

ADDITIONAL_POSTS_AMOUNT = 1
POSTS_NUM = POSTS_AMOUNT + ADDITIONAL_POSTS_AMOUNT
GROUP_POSTS_NUM = POSTS_NUM


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='noname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='another-test-slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create([
            Post(
                text='Тестовый пост' + str(num),
                group=cls.group,
                author=cls.user,
            ) for num in range(1, POSTS_NUM + 1)
        ])
        cls.post = Post.objects.get(pk=1)
        cls.all_posts = Post.objects.all()

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTest.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': PostPagesTest.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={
                    'username': PostPagesTest.user.username
                }
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': PostPagesTest.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': PostPagesTest.post.pk}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """В шаблоны передаётся соответствующий контекст."""
        pages_context = {
            reverse('posts:index'): {
                'page_obj': list(PostPagesTest.all_posts)[:POSTS_AMOUNT],
            },
            reverse('posts:index') + '?page=2': {
                'page_obj': list(
                    PostPagesTest.all_posts
                )[POSTS_AMOUNT:POSTS_NUM],
            },
            reverse(
                'posts:group_list', kwargs={'slug': PostPagesTest.group.slug}
            ): {
                'page_obj': list(
                    PostPagesTest.all_posts.filter(group=PostPagesTest.group)
                )[:POSTS_AMOUNT],
                'group': PostPagesTest.group,
            },
            reverse(
                'posts:group_list', kwargs={'slug': PostPagesTest.group.slug}
            ) + '?page=2': {
                'page_obj': list(
                    PostPagesTest.all_posts.filter(group=PostPagesTest.group)
                )[POSTS_AMOUNT:GROUP_POSTS_NUM],
            },
            reverse('posts:profile', kwargs={
                'username': PostPagesTest.user.username
            }): {
                'page_obj': list(
                    PostPagesTest.all_posts.filter(author=PostPagesTest.user)
                )[:POSTS_AMOUNT],
                'author': PostPagesTest.user,
                'posts_num': PostPagesTest.all_posts.filter(
                    author=PostPagesTest.user
                ).count(),
            },
            reverse('posts:post_detail', kwargs={
                'post_id': PostPagesTest.post.pk
            }): {
                'post': PostPagesTest.post,
            },
            reverse('posts:post_create'): {
                'form': {
                    'type': PostForm,
                    'fields_type': {
                        'text': forms.fields.CharField,
                        'group': forms.models.ModelChoiceField,
                        'image': forms.fields.ImageField,
                    },
                },
            },
            reverse('posts:post_edit', kwargs={
                'post_id': PostPagesTest.post.pk
            }): {
                'form': {
                    'type': PostForm,
                    'fields_type': {
                        'text': forms.fields.CharField,
                        'group': forms.models.ModelChoiceField,
                        'image': forms.fields.ImageField,
                    },
                    'fields_value': {
                        'text': PostPagesTest.post.text,
                        'group': PostPagesTest.post.group.pk,
                        'image': PostPagesTest.post.image,
                    }
                },
                'is_edit': True,
            },
        }
        for reverse_name, key_context in pages_context.items():
            with self.subTest(reverse_name=reverse_name):
                for key, expected_context in key_context.items():
                    with self.subTest(key=key):
                        response = self.authorized_client.get(reverse_name)
                        self.assertIn(key, response.context)
                        if key == 'page_obj':
                            self.assertEqual(
                                response.context[key].object_list,
                                expected_context
                            )
                        elif key == 'form':
                            self.assertIn('type', expected_context)
                            self.assertIn('fields_type', expected_context)
                            self.assertIsInstance(
                                response.context[key],
                                expected_context['type']
                            )
                            for field, expected_type in expected_context[
                                'fields_type'
                            ].items():
                                with self.subTest(field=field):
                                    self.assertIsInstance(
                                        response.context['form'].fields.get(
                                            field
                                        ),
                                        expected_type
                                    )
                            if 'fields_value' in expected_context:
                                for field, expected_value in expected_context[
                                    'fields_value'
                                ].items():
                                    with self.subTest(field=field):
                                        self.assertEqual(
                                            response.context[
                                                'form'
                                            ].initial[field],
                                            expected_value
                                        )
                        else:
                            self.assertEqual(
                                response.context[key],
                                expected_context
                            )

    def test_post_with_group_shown_on_desired_pages(self):
        """Пост с группой отображается на желаемых страницах."""
        desired_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={
                'slug': PostPagesTest.group.slug
            }),
            reverse('posts:profile', kwargs={
                'username': PostPagesTest.user.username
            }),
        ]
        for page in desired_pages:
            response = self.authorized_client.get(page)
            try:
                self.assertIn(
                    PostPagesTest.post,
                    response.context['page_obj']
                )
            except AssertionError:
                page += '?page=2'
                response = self.authorized_client.get(page)
                self.assertIn(
                    PostPagesTest.post,
                    response.context['page_obj']
                )

    def test_post_with_group_not_shown_on_other_group_page(self):
        """Пост с группой не отображается на странице другой группы."""
        reverse_name = reverse('posts:group_list', kwargs={
            'slug': PostPagesTest.another_group.slug
        })
        response = self.authorized_client.get(reverse_name)
        self.assertNotIn(
            PostPagesTest.post,
            response.context['page_obj']
        )

    def test_follow(self):
        """При подписке авторизованного пользователя на другого автора
        создаётся запись в бд."""
        author = User.objects.create(username='author')
        reverse_name = reverse('posts:profile_follow', kwargs={
            'username': author.username
        })
        redirect_reverse_name = reverse('posts:profile', kwargs={
            'username': author.username
        })
        response = self.authorized_client.get(reverse_name)
        self.assertTrue(Follow.objects.filter(
            user=PostPagesTest.user,
            author=author
        ).exists())
        self.assertRedirects(response, redirect_reverse_name)

    def test_self_follow(self):
        """Авторизованный пользователь не может подписаться на себя."""
        reverse_name = reverse('posts:profile_follow', kwargs={
            'username': PostPagesTest.user.username
        })
        redirect_reverse_name = reverse('posts:profile', kwargs={
            'username': PostPagesTest.user.username
        })
        response = self.authorized_client.get(reverse_name)
        self.assertFalse(Follow.objects.filter(
            user=PostPagesTest.user,
            author=PostPagesTest.user
        ).exists())
        self.assertRedirects(response, redirect_reverse_name)

    def test_unfollow(self):
        """При отписке авторизованного пользователя от отслеживаемого автора
        запись в бд удаляется."""
        author = User.objects.create(username='author')
        Follow.objects.create(user=PostPagesTest.user, author=author)
        reverse_name = reverse('posts:profile_unfollow', kwargs={
            'username': author.username
        })
        redirect_reverse_name = reverse('posts:profile', kwargs={
            'username': author.username
        })
        response = self.authorized_client.get(reverse_name)
        self.assertFalse(Follow.objects.filter(
            user=PostPagesTest.user,
            author=author
        ).exists())
        self.assertRedirects(response, redirect_reverse_name)

    def test_favorite_authors_page(self):
        """Новый пост автора отображается на странице Избранного у
        подписчиков."""
        author = User.objects.create(username='author')
        author_post = Post.objects.create(
            text='Пост автора',
            author=author,
        )
        Follow.objects.create(user=PostPagesTest.user, author=author)
        reverse_name = reverse('posts:follow_index')
        response = self.authorized_client.get(reverse_name)
        self.assertIn(author_post, response.context['page_obj'])

    def test_favorite_authors_page(self):
        """Новый пост автора не отображается на странице Избранного у
        не подписанных пользователей."""
        author = User.objects.create(username='author')
        author_post = Post.objects.create(
            text='Пост автора',
            author=author,
        )
        reverse_name = reverse('posts:follow_index')
        response = self.authorized_client.get(reverse_name)
        self.assertNotIn(author_post, response.context['page_obj'])

    def test_cache(self):
        """Тест работы кэша."""
        post = Post.objects.create(text='пост', author=PostPagesTest.user)
        response = self.authorized_client.get(reverse('posts:index'))
        cached_content = response.content
        self.assertEqual(response.content, cached_content)
        post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, cached_content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, cached_content)
