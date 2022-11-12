import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.auth_user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='The title',
            slug='test slug',
            description='Some f_definitions'
        )
        cls.post = Post.objects.create(
            author=cls.auth_user,
            group=cls.group,
            text='Проверка поста',
            image=uploaded
        )

    def setUp(self):
        self.non_auth_user = Client()
        self.user = User.objects.create_user(username='Auth')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.authorized_auth_client = Client()
        self.authorized_auth_client.force_login(self.auth_user)

    def test_context_used_correct_index_and_grouplist(self):
        """Шаблон index сформирован с правильным контекстом."""
        pages_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        ]
        for reserve_name in pages_list:
            with self.subTest(reserve_name=reserve_name):
                response = self.authorized_user.get(reserve_name)
                self.assertEqual(
                    response.context['page_obj'][0].text, 'Проверка поста'
                )
                self.assertEqual(
                    response.context['page_obj'][0].author.username, 'auth'
                )
                self.assertEqual(
                    response.context['page_obj'][0].group.title, 'The title'
                )

    def test_one_post_filtered_by_id(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_user.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_object = response.context.get('post')
        post_by_id = first_object.text
        id_in_post = first_object.id
        self.assertEqual(post_by_id, 'Проверка поста')
        self.assertEqual(id_in_post, self.post.id)

    def test_post_edit_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_auth_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_another_group(self):
        """Пост не попал в другую группу."""
        response = self.authorized_user.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertTrue(post_text_0, 'Проверка поста')

    def test_post_another_profile(self):
        """Пост в профайле пользователя."""
        response = self.authorized_user.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            )
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertTrue(post_text_0, 'Проверка поста')

    def test_post_on_main_page(self):
        """Пост на главной странице сайта."""
        response = self.authorized_user.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertTrue(post_text_0, 'Проверка поста')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='The title',
            slug='test slug',
            description='Some f_definitions'
        )

        Post.objects.bulk_create(Post(
            text=f'Новый пост без группы {post}',
            group=cls.group,
            author=cls.user,)
            for post in range(13)
        )

    def setUp(self):
        self.non_auth_user = Client()
        self.user = User.objects.create_user(username='Auth')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_first_pages(self):
        first_pages_with_paginator = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        ]
        for pages in first_pages_with_paginator:
            with self.subTest(pages=pages):
                response = self.authorized_user.get(pages)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_pages(self):
        second_pages_with_paginator = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        ]
        for pages in second_pages_with_paginator:
            with self.subTest(pages=pages):
                response = self.authorized_user.get(pages, {'page': 2})
            self.assertEqual(len(response.context['page_obj']), 3)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        response_first_content = response.content
        Post.objects.all().delete()
        response = self.authorized_client.get(reverse('posts:index'))
        response_second_content = response.content
        self.assertEquals(response_first_content, response_second_content)

    def test_cashe_second(self):
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        response_first_content = response.content
        Post.objects.all().delete()
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        response_second_content = response.content
        self.assertNotEqual(response_first_content, response_second_content)


class FollowTests(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(username='follower')
        self.user_following = User.objects.create_user(username='following')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Test for checking feed'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow_auth_user(self):
        """Авторизованный пользователь может подписываться"""
        self.client_auth_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_following.username}
            )
        )
        follow_last = Follow.objects.last()
        self.assertEqual(follow_last.user.username, 'follower')
        self.assertEqual(follow_last.author.username, 'following')

    def test_unfollow_auth_user(self):
        """Авторизованный пользователь может отписываться"""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        self.client_auth_follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_following.username}
            )
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_new_post_for_followers(self):
        """Запись появляется у подписанных."""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response_follower = self.client_auth_follower.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_follower.context['page_obj']), 1)

    def test_no_new_post_for_followers(self):
        """Запись не появляется у неподписанных."""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response_non_follower = self.client_auth_following.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_non_follower.context['page_obj']), 0)
