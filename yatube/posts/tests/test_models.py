from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост на 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models_str = (
            (self.post, self.post.text[:15]),
            (self.group, self.group.title)
        )
        for field, expected_value in models_str:
            with self.subTest(field=field):
                self.assertEqual(str(field), expected_value)

    def test_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        field_verboses = (
            ('text', 'Текст поста'),
            ('pub_date', 'Дата публикации'),
            ('author', 'Автор'),
            ('group', 'Группа')
        )
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value
                )
