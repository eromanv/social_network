from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass(cls)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Проверка поста',
        )
        cls.group = Group.objects.create(
            title='The title',
            slug='test slug',
            description='Some f_definitions'
        )

    def setUp(self):
        self.non_auth_user = Client()
        self.user = User.objects.create_user(username='Auth')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def templates_for_urls_accebility(self):
        templates_urls = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/slug/',
            'posts/profile.html': '/profile/username/',
            'posts/post_detail.html': '/posts/post_id/',
        }
        for template, adress in templates_urls.items():
            with self.subTest(adress=adress):
                response = self.non_auth_user.get(adress)
                self.assertEqual(response.status_code, 200)

    def mistake404(self):
        response = self.guest_client.get('unexisting_page')
        self.assertEqual(response.status_code, 404)

    def post_createcheck(self):
        response = self.authorized_user.get('/create/')
        self.assertEqual(response.status_code, 200)

    def post_editcheck(self):
        response = self.user.get('/create/')
        self.assertEqual(response.status_code, 200)
