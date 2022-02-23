from django.test import TestCase
from ..models import Post, Group, User, CHAR_NUM


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Пост' * CHAR_NUM,
            author=cls.user,
        )

    def test_post_objects_have_correct_names(self):
        '''У объектов кастомных моделей корректно работает __str__.'''
        expected_data = {
            PostModelTest.post: PostModelTest.post.text[:CHAR_NUM],
            PostModelTest.group: PostModelTest.group.title,
        }
        for obj, expected_value in expected_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(str(obj), expected_value)

    def test_verbose_name(self):
        '''У объектов модели Post корректно отображается verbose_name.'''
        post = PostModelTest.post
        fields_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'created': 'Дата создания',
            'group': 'Группа',
        }

        for field, expected_value in fields_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        '''У объектов модели Post корректно отображается help_text.'''
        post = PostModelTest.post
        fields_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }

        for field, expected_value in fields_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
