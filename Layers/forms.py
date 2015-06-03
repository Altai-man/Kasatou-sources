from django import forms
from Layers.models import User, Thread, Post


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('email', 'password', 'name', 'theme', 'thread_per_page')


class ThreadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ThreadForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Thread
        fields = ['topic', 'text', 'image1', 'image2',
                  'archive', 'board_id', 'user_id']


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ['topic', 'text', 'image1', 'image2', 'image3',
                  'archive', 'thread_id', 'board_id', 'user_id']
