import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls.base import reverse

from ..models import Post, Group, Comment, User
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='noname')
        cls.group = Group.objects.create(
            title='Группа для поста',
            slug='test-slug',
            description='Описание',
        )
        cls.super_group = Group.objects.create(
            title='Группа для супер-поста',
            slug='super-slug',
            description='Супер-описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)

    def test_create_post(self):
        '''При отправке поста через форму PostForm
        создаётся запись в базе данных'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': PostFormTest.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        expected_data = {
            'pk': 2,
            'text': form_data['text'],
            'group': PostFormTest.group,
            'author': PostFormTest.user,
        }
        latest_post = Post.objects.latest()
        for field, expected_value in expected_data.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(latest_post, field), expected_value
                )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostFormTest.user.username}
        ))

    def test_create_post_with_image(self):
        '''При отправке поста с картинкой через форму PostForm
        создаётся запись в базе данных'''
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новый пост',
            'group': PostFormTest.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        expected_data = {
            'pk': 2,
            'text': form_data['text'],
            'group': PostFormTest.group,
            'author': PostFormTest.user,
            'image': small_gif,
        }
        latest_post = Post.objects.latest()
        for field, expected_value in expected_data.items():
            with self.subTest(field=field):
                if field == 'image':
                    self.assertEqual(
                        getattr(latest_post, field).read(), expected_value
                    )
                else:
                    self.assertEqual(
                        getattr(latest_post, field), expected_value
                    )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostFormTest.user.username}
        ))

    def test_create_post(self):
        '''Неаторизованный пользователь не может добавить пост'''
        posts_count = Post.objects.count()
        response = self.guest_client.post(
            reverse('posts:post_create'),
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, reverse(
            'users:login') + '?next=/create/'
        )

    def test_edit_post(self):
        '''При редактировании поста в модели Post запись с post_id
        изменяется'''
        posts_count = Post.objects.count()
        post = PostFormTest.post
        form_data = {
            'text': 'Супер-тестовый пост',
            'group': PostFormTest.super_group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.latest()
        expected_data = {
            'pk': post.pk,
            'text': form_data['text'],
            'group': PostFormTest.super_group,
            'author': PostFormTest.user,
        }
        for field, expected_value in expected_data.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(edited_post, field), expected_value
                )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.pk}
        ))


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='noname')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentFormTest.user)

    def test_authorized_user_can_add_comment(self):
        """После успешной отправки комментарий сохраняется в бд
        и появяется на странице."""
        comments_count = Comment.objects.count()
        post = CommentFormTest.post
        reverse_name = reverse('posts:add_comment', kwargs={
            'post_id': post.pk
        })
        form_data = {
            'text': 'Тестовый комментарий'
        }
        expected_data = {
            'post': post,
            'text': form_data['text'],
            'author': CommentFormTest.user,
        }
        response = self.authorized_client.post(
            reverse_name,
            data=form_data,
            follow=True
        )
        latest_comment = Comment.objects.latest()
        for field, expected_value in expected_data.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(latest_comment, field), expected_value
                )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': post.pk
        }))

    def test_anonymous_user_can_not_add_comment(self):
        """Неавторизованный пользователь не может отправить комментарий."""
        comments_count = Comment.objects.count()
        post = CommentFormTest.post
        reverse_name = reverse('posts:add_comment', kwargs={
            'post_id': post.pk
        })
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.guest_client.post(
            reverse_name,
            data=form_data,
            follow=True
        )
        self.assertFalse(Comment.objects.filter(
            text=form_data['text'], post=post).exists()
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertRedirects(response, reverse(
            'users:login') + f'?next=/posts/{post.pk}/comment/')
