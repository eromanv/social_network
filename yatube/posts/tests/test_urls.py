from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='The title',
            slug='test slug',
            description='Some f_definitions'
        )
        cls.post = Post.objects.create(
            author=cls.auth_user,
            text='Проверка поста',
            group=cls.group,
        )

    def setUp(self):
        self.non_auth_user = Client()
        self.user = User.objects.create_user(username='Auth')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.authorized_auth_client = Client()
        self.authorized_auth_client.force_login(self.auth_user)

    def test_pages_uses_correct_template(self):
        """Обращение по адресу name:namespace соостветствует шаблонам."""
        templates_urls = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug
            }): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.user
            }): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id
            }): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id,
            }): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_urls.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_mistake404(self):
        response = self.non_auth_user.get('unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_createcheck(self):
        response = self.authorized_user.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_editcheck(self):
        response = self.non_auth_user.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
