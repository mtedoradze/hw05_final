from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    """Данные для тестирования.
    Создание экземпляра тестового поста."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author
        )
        cls.common_urls_templates = (
            (
                reverse('posts:index'),
                'posts/index.html'
            ),
            (
                reverse('posts:group_list', args=(cls.group.slug,)),
                'posts/group_list.html'
            ),
            (
                reverse('posts:profile', args=(cls.user_author,)),
                'posts/profile.html'
            ),
            (
                reverse('posts:post_detail', args=(cls.post.id,)),
                'posts/post_detail.html'
            )
        )
        cls.create_url_template = (
            (reverse('posts:post_create'), 'posts/post_create.html'),
        )
        cls.edit_url_template = (
            (
                reverse('posts:post_edit', args=(cls.post.id,)),
                'posts/post_create.html'
            ),
        )

    def setUp(self):
        """Данные для тестирования.
        Создание экземпляров клиента:
        неавторизованного и авторизованного."""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Authorized_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_accessability_templates_redirects_for_anonimous(self):
        """Проверка доступности страниц, шаблонов доступных страниц
        и редиректов недоступных страниц для анонимного пользователя."""
        for url, template in PostsURLTests.common_urls_templates:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )
                self.assertTemplateUsed(response, template)

        redirect_reverse = reverse('users:login')
        for url, template in PostsURLTests.create_url_template:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.FOUND
                )
                self.assertRedirects(
                    response,
                    f'{redirect_reverse}?next={url}'
                )

        for url, template in PostsURLTests.edit_url_template:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.FOUND
                )
                self.assertRedirects(
                    response,
                    f'{redirect_reverse}?next={url}'
                )

    def test_pages_accessability_templates_redirects_for_authorized(self):
        """Проверка доступности страниц, шаблонов доступных страниц
        и редиректов недоступных страниц для авторизованного пользователя."""
        for url, template in PostsURLTests.common_urls_templates:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )
        for url, template in PostsURLTests.create_url_template:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )
                self.assertTemplateUsed(response, template)

        for url, template in PostsURLTests.edit_url_template:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.FOUND
                )
                self.assertRedirects(
                    response,
                    reverse('posts:post_detail', args=(PostsURLTests.post.id,))
                )

    def test_pages_accessability_templates_for_author(self):
        """Проверка доступности страниц и их шаблонов для автора поста
        (редиректов нет)."""
        self.author = Client()
        self.author.force_login(self.user_author)
        for url, template in PostsURLTests.common_urls_templates:
            with self.subTest(url=url):
                response = self.author.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )
        for url, template in PostsURLTests.create_url_template:
            with self.subTest(url=url):
                response = self.author.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )

        for url, template in PostsURLTests.edit_url_template:
            with self.subTest(url=url):
                response = self.author.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        """Проверка несуществующей страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
