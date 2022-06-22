from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

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
            ('/', 'posts/index.html'),
            ('/group/test_slug/', 'posts/group_list.html'),
            ('/profile/test_author/', 'posts/profile.html'),
            ('/posts/1/', 'posts/post_detail.html')
        )
        cls.create_url_template = (
            ('/create/', 'posts/post_create.html'),
        )
        cls.edit_url_template = (
            ('/posts/1/edit/', 'posts/post_create.html'),
        )

    def setUp(self):
        """Данные для тестирования.
        Создание экземпляров клиента:
        неавторизованного и авторизованного."""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Authorized_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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

        for url, template in PostsURLTests.create_url_template:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.FOUND
                )
                self.assertRedirects(response, '/auth/login/?next=/create/')

        for url, template in PostsURLTests.edit_url_template:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.FOUND
                )
                self.assertRedirects(
                    response, '/auth/login/?next=/posts/1/edit/'
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
                self.assertRedirects(response, '/posts/1/')

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
