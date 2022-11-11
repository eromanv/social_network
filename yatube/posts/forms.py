from django import forms

from posts.models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Картинка, которую можно показать'
        }
        labels = {
            'text': 'Текст нового поста',
            'group': 'Группа',
            'image': 'Картинка'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
