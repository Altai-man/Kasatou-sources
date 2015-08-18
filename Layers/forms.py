"""Forms for Kasatou."""
from django import forms
from Layers.models import User, Thread, Post


class UserForm(forms.ModelForm):
    """Form for registration. Contains email, password and theme."""
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

    class Meta:
        """Meta-class for UserForm."""
        model = User
        fields = ('email', 'password', 'theme')


class ThreadForm(forms.ModelForm):
    """Form for thread creation.
    Contains topic, text, images, archive, board_id and user_id.
    """
    def __init__(self, *args, **kwargs):
        super(ThreadForm, self).__init__(*args, **kwargs)

    class Meta:
        """Meta-class for ThreadForm."""
        model = Thread
        fields = ['topic', 'text', 'image1', 'image2',
                  'archive', 'board_id', 'user_id']


class PostForm(forms.ModelForm):
    """Form for post creation.
    Contains topic, text, images, archive, board_id and user_id.
    """
    def clean(self):
        """Custom check for form. Forbids empty posts."""
        form = super(PostForm, self).clean()
        try:  # Our custom error.
            # We use try, because clean of superclass can exclude some fields.
            if not any([form['topic'], form['image1'], form['text']]):
                msg = "You should fill text field or image field"
                self.add_error('thread_id', msg)
        except KeyError:
            pass

    class Meta:
        """Meta-class for PostForm."""
        model = Post
        fields = ['topic', 'text', 'image1', 'image2', 'image3',
                  'archive', 'thread_id', 'board_id', 'user_id']
