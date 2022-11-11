import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
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
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.non_auth_user = Client()
        self.user = User.objects.create_user(username='Auth')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.authorized_auth_client = Client()
        self.authorized_auth_client.force_login(self.auth_user)

    def test_form_create_post(self):
        """Валидная форма создает пост."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small_gr.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test title form',
            'group': self.group.id,
            'author': self.post.author,
            'image': uploaded,
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user
        }))
        last_objects = Post.objects.last()
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(last_objects.text, 'Test title form')
        self.assertEqual(last_objects.group.title, 'The title')
        self.assertEqual(last_objects.author.username, 'Auth')
        self.assertTrue(last_objects, form_data['image'])

    def test_form_post_edit(self):
        """При отправке валидной формы меняется пост с post_id в БД."""
        post_new = Post.objects.get(id=self.post.id)
        form_data = {
            'text': 'Измененный пост',
            'group': self.group.id,
            'author': self.post.author,
        }
        response = self.authorized_auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_new.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post_new.id}),
        )
        post2 = Post.objects.get(id=self.post.id)
        self.assertEqual(post2.text, 'Измененный пост')
        self.assertEqual(post2.group.title, 'The title')
        self.assertEqual(post2.author.username, 'auth')


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Проверка поста',
        )
        cls.form = CommentForm()

    def setUp(self):
        self.non_auth_user = Client()
        self.user = User.objects.create_user(username='ForCommentTest')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_auth_user_comment_appeares(self):
        """Комментарий появляется на странице поста."""
        self.authorized_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={
                'text': 'Test comment form',
                'author': self.user,
            },
            follow=True
        )
        comment_last = Comment.objects.last()
        self.assertEqual(comment_last.text, 'Test comment form')
        self.assertEqual(comment_last.author.username, 'ForCommentTest')

    def test_non_auth_user_comment(self):
        """Комментировать посты может только авторизованный пользователь."""
        self.non_auth_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': 'Test comment forms'},
            follow=True
        )
        response = self.non_auth_user.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.authorized_user.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertNotContains(response, 'Test comment forms')


