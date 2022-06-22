from http import HTTPStatus
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Post, Group, Follow
from posts.forms import PostForm

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
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
            author=cls.user_author,
            group=cls.group
        )
        cls.index_url_template = (
            (reverse('posts:index'),
             'posts/index.html'),
        )
        cls.group_list_url_template = (
            (reverse('posts:group_list', args=(cls.group.slug,)),
             'posts/group_list.html'),
        )
        cls.profile_url_template = (
            (reverse('posts:profile', args=(cls.user_author,)),
             'posts/profile.html'),
        )
        cls.post_detail_url_template = (
            (reverse('posts:post_detail', args=(cls.post.id,)),
             'posts/post_detail.html'),
        )
        cls.post_edit_url_template = (
            (reverse('posts:post_edit', args=(cls.post.id,)),
             'posts/post_create.html'),
        )
        cls.post_create_url_template = (
            (reverse('posts:post_create'),
             'posts/post_create.html'),
        )
        cls.all_urls = (
            cls.index_url_template,
            cls.group_list_url_template,
            cls.profile_url_template,
            cls.post_detail_url_template,
            cls.post_edit_url_template,
            cls.post_create_url_template
        )
        cls.paginated_urls = (
            cls.index_url_template,
            cls.group_list_url_template,
            cls.profile_url_template
        )
        cls.post_create_edit_urls = (
            cls.post_edit_url_template,
            cls.post_create_url_template
        )
        cls.form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.fields.ChoiceField),
            ('image', forms.fields.ImageField)
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Данные для тестирования.
        Создание экземпляров авторизованного пользователя
        и автора поста."""
        self.user_author = User.objects.get(username='test_author')
        self.author = Client()
        self.author.force_login(self.user_author)
        self.user = User.objects.create_user(username='Authorized_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_all_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for object in PostsPagesTests.all_urls:
            for url, template in object:
                with self.subTest(url=url):
                    response = self.author.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertTemplateUsed(response, template)

    def test_group_profile_pages_show_correct_context(self):
        """Шаблоны страниц index, group_list и profile
        сформированы с правильным контекстом.
        Пост с группой появляется на страницах:
        index, group_list, profile."""
        for object in PostsPagesTests.paginated_urls:
            for url, template in object:
                with self.subTest(url=url):
                    response = self.author.get(url)
                    self.post_first = response.context['page_obj'][0]
                    self.assertEqual(
                        self.post_first.text, PostsPagesTests.post.text
                    )
                    self.assertEqual(
                        self.post_first.group, PostsPagesTests.post.group
                    )
                    self.assertEqual(
                        self.post_first.author, PostsPagesTests.post.author
                    )
                    self.assertEqual(
                        self.post_first.pub_date, PostsPagesTests.post.pub_date
                    )

    def test_forms_post_create_edit_show_correct_context(self):
        """Шаблоны форм post_create и post_edit сформированы
        с правильным контекстом."""
        for object in PostsPagesTests.post_create_edit_urls:
            for url, template in object:
                response = self.author.get(url)
                self.assertIsInstance(response.context.get('form'), PostForm)
                for value, expected in PostsPagesTests.form_fields:
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            'form').fields.get(value)
                        self.assertIsInstance(form_field, expected)
        response_post_edit = self.author.get(
            reverse('posts:post_edit', args=(PostsPagesTests.post.id,))
        )
        self.assertEqual(response_post_edit.status_code, HTTPStatus.OK)
        self.assertIn('is_edit', response_post_edit.context)

    def test_post_with_group_appears_not_on_wrong_pages(self):
        """Пост с группой не появляется на странице другой группы."""
        self.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )
        self.post_with_group_2 = Post.objects.create(
            text='Тестовый текст',
            author=self.user_author,
            group=self.group_2
        )
        response = self.author.get(reverse(
            'posts:group_list',
            args=(self.group_2.slug,)
        )
        )
        self.post_first = response.context['page_obj'][0]
        self.assertNotEqual(self.post_first.group, self.post.group)

    def post_with_pic_appears_on_pages(self):
        """Проверка, что при выводе поста с картинкой, изображение
        передаётся в словаре context на страницы:
        index, profile, group_list, post_detail"""
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
        post_with_pic = Post.objects.create(
            text='Текст с картинкой',
            author=self.user_author,
            group=self.group,
            image=uploaded
        )
        for url in self.urls_paginator:
            with self.subTest(url=url):
                response = self.author.get(url)
                self.post_first = response.context['page_obj'][0]
                self.assertEqual(self.post_first.text, 'Текст с картинкой')
                self.assertEqual(self.post_first.image, 'posts/small.gif')
        response_post_detail = self.author.get(reverse
                                               (
                                                   'posts:post_detail',
                                                   args=(post_with_pic.id,)
                                               )
                                               )
        post_detail = response_post_detail.context['post']
        self.assertEqual(post_detail.image, 'posts/small.gif')

    def test_first_page_contains_ten_records(self):
        """Проверка паджинатора: количество постов
        на первой странице равно 10, на второй странице равно 2."""
        for i in range(11):
            self.post = Post.objects.bulk_create([
                Post(
                    text=f'Текст {i+1}',
                    author=PostsPagesTests.user_author,
                    group=PostsPagesTests.group
                )
            ])
        for object in PostsPagesTests.paginated_urls:
            for url, template in object:
                with self.subTest(url=url):
                    response_first_page = self.author.get(url)
                    response_second_page = self.author.get(
                        url + '?page=2'
                    )
                    self.assertEqual
                    (
                        len(response_first_page.context['page_obj']),
                        10
                    )
                    self.assertEqual
                    (
                        len(response_second_page.context['page_obj']),
                        2
                    )

    def test_comments_accessability_for_anonimous(self):
        """Проверка, что комментировать посты может только
        авторизованный пользователь."""
        self.guest_client = Client()
        response_guest = self.guest_client.get('/posts/1/comment/')
        response_authorized = self.authorized_client.get(
            reverse('posts:add_comment', args=(PostsPagesTests.post.id,))
        )
        self.assertRedirects(
            response_guest, '/auth/login/?next=/posts/1/comment/'
        )
        self.assertRedirects(
            response_authorized, '/posts/1/'
        )

    def test_index_page_cache(self):
        """Проверка кеширования главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        PostsPagesTests.post.delete()
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn(PostsPagesTests.post.text, response.content.decode())
        cache.clear()
        response_second = self.authorized_client.get(reverse('posts:index'))
        self.assertNotIn(
            PostsPagesTests.post.text,
            response_second.content.decode()
        )

    def test_follow_unfollow_functions(self):
        """Проверка подписок: авторизованный пользователь
        может подписываться на других пользователей
        и удалять их из подписок."""
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            args=(PostsPagesTests.post.author.username, )
        )
        )
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(
            Follow.objects.first().author,
            PostsPagesTests.post.author
        )
        self.assertEqual(Follow.objects.first().user, self.user)
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            args=(PostsPagesTests.post.author.username, )
        )
        )
        self.assertEqual(Follow.objects.count(), 1)
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            args=(PostsPagesTests.post.author.username, )
        )
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_following_posts_appear_on_followers_pages_only(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан."""
        self.new_user = User.objects.create_user(username='New_user')
        self.new_authorized_client = Client()
        self.new_authorized_client.force_login(self.new_user)
        new_post = Post.objects.create(
            text='Новый пост',
            author=PostsPagesTests.user_author,
            group=PostsPagesTests.group
        )
        Follow.objects.create(
            author=new_post.author,
            user=self.user
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            response.context['page_obj'][0].author,
            new_post.author
        )
        response = self.new_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(new_post.author.username, response.context)

    def test_follower_cannot_follow_himself(self):
        """Проверка подписок: нельзя подписаться на самого себя."""
        self.author.get(reverse(
            'posts:profile_follow',
            args=(PostsPagesTests.post.author.username, )
        )
        )
        self.assertEqual(Follow.objects.count(), 0)
