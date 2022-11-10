from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group

User = get_user_model()


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Проверка поста' * 3,
        )
        cls.group = Group.objects.create(
            title='The title',
            slug='test slug',
            description='Some f_definitions'
        )

    def test_check_the_title(self):
        post = PostsModelTest.post
        post_ordered = post.text[:15]
        self.assertEqual(post_ordered, str(post)[:15])

    def test_check_the_group(self):
        group_title = PostsModelTest.group.title
        self.assertEqual(group_title, 'The title')
