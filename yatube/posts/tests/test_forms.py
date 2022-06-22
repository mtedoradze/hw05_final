import shutil
import tempfile

from django.contrib.auth import get_user_model
from posts.forms import CommentForm
from posts.models import Post, Group
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Данные для тестирования.
        Создание экземпляра группы."""
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Данные для тестирования.
        Создание экземпляра авторизованного пользователя."""
        self.user = User.objects.create_user(username='Authorized_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post (с картинкой).
        Пользователь авторизован."""
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
            'text': 'Новый текст из формы',
            'group': PostModelTest.group.id,
            'author': self.user,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().text, 'Новый текст из формы')
        self.assertEqual(Post.objects.first().group, PostModelTest.group)
        self.assertEqual(Post.objects.first().author, self.user)
        self.assertEqual(Post.objects.first().image, 'posts/small.gif')
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user,))
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись и сохраняет ее в Post.
        Пользователь - автор поста."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=PostModelTest.group
        )
        self.posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст из формы',
            'author': self.user,
            'group': PostModelTest.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), self.posts_count)
        self.assertEqual(Post.objects.first().text, 'Новый текст из формы')
        self.assertEqual(Post.objects.first().author, self.user)
        self.assertEqual(Post.objects.first().group, PostModelTest.group)

    def test_post_creation_for_anonimous(self):
        """Неавторизованный пользователь не может создать пост."""
        self.guest_client = Client()
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=/create/'
        )

    def test_comment_appears_on_post_detail_page(self):
        """Проверка формы для комментариев -
        после успешной отправки комментарий появляется
        на странице поста."""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост'
        )
        form_data = {
            'author': self.user,
            'post': post,
            'text': 'Комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=(post.id,)),
            data=form_data,
            follow=True
        )
        response_post_detail = self.authorized_client.get(
            reverse('posts:post_detail', args=(post.id,))
        )
        self.assertIsInstance(
            response.context['form'], CommentForm
        )
        self.assertEqual(
            str(response_post_detail.context['comments'][0].text),
            form_data['text']
        )
