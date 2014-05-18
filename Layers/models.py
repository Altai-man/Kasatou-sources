#! -*- coding: utf-8 -*-
# Pyhon
import os
from PIL import Image
import re
import random
import string

# Django
from django import forms
from django.db import models
from django.utils.html import escape
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models.signals import pre_delete, post_save, pre_save
from django.dispatch import receiver
from Kasatou.settings import PIC_SIZE, MEDIA_ROOT


class SearchManager(models.Manager):
    def search(self, search_text):
        search_text = escape(search_text)  # Escape HTML symbols.
        query = self.filter(text__icontains=search_text)
        return query


class UserManager(BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=UserManager.normalize_email(email),)
        user.set_password(password)  # Create hash, not plain text.
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        superuser = self.create_user(email, password)
        superuser.is_admin = True
        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    email = models.EmailField(_('Email'), max_length=255, unique=True)
    theme = models.CharField(max_length=10, default="Light")
    name = models.CharField(max_length=14, default='Anonymous')
    thread_per_page = models.IntegerField(default=8)
    date_joined = models.DateTimeField(_('Date joined'), default=timezone.now)
    invites_count = models.IntegerField(default=3)

    is_admin = models.BooleanField(_('Admin status'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('Anonymous')
        verbose_name_plural = _('Anonymouses')

    def get_short_name(self):
        return self.name

    # Permissions not used, so we can not write this functions.
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('email', 'password', 'name', 'theme', 'thread_per_page')


class Invite(models.Model):
    is_active = models.BooleanField(default=True)
    code = models.CharField(max_length=32)
    sender = models.ForeignKey(User)

    def generate_code(self):
        self.code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(32))

    def check(self, code):
        try:
            curr_invite = Invite.objects.get(code=code)
        except:
              curr_invite = None

        if curr_invite is not None:
            curr_invite.is_active = False
            return True
        else:
            return False

    def __str__(self):
        return 'Invite№ %s.' % self.id


class Board(models.Model):
    board_name = models.CharField(max_length=3)
    thread_max_post = models.IntegerField(default=500)
    is_moderated = models.BooleanField(default=True)  # Can user delete posts?

    def get_board_view(self):
        threads = Thread.objects.filter(board_id=self).order_by('-update_time')
        return [dict(thread=th, posts=th.latest_posts()) for th in threads]

    def __str__(self):
        return '/%s/' % self.board_name


class BasePost(models.Model):
    objects = SearchManager()

    text = models.TextField(max_length=5000, blank=True)
    date = models.DateTimeField('%Y-%m-%d %H:%M:%S', auto_now_add=True)
    archive = models.FileField(upload_to='documents', blank=True)
    board_id = models.ForeignKey(Board)
    user_id = models.ForeignKey(User)

    def make_thumbnail(self):
        if self.image1:
            ratio = min(PIC_SIZE/self.image1.height,
                        PIC_SIZE/self.image1.width)
            thumbnail = Image.open(self.image1.path)
            thumbnail.thumbnail((int(self.image1.width*ratio),
                                 int(self.image1.height*ratio)),
                                Image.ANTIALIAS)
            thumbnail.save(''.join([MEDIA_ROOT, '/thumbnails/', self.image1.name]), thumbnail.format)
        if self.image2:
            ratio = min(PIC_SIZE/self.image2.height,
                        PIC_SIZE/self.image2.width)
            thumbnail = Image.open(self.image2.path)
            thumbnail.thumbnail((int(self.image2.width*ratio),
                                 int(self.image2.height*ratio)),
                                Image.ANTIALIAS)
            thumbnail.save(''.join([MEDIA_ROOT, '/thumbnails/', self.image2.name]), thumbnail.format)
            return True
        else:
            return False

    @staticmethod
    def markup(string):
        """ Makes markup for post and thread text. Strings will be safe. """
        string = escape(string)
        markups = [
            # quote
            [r'(?P<text>(?<!(&gt;))&gt;(?!(&gt;)).+)',
             r'<span class="post_quote">\g<text></span>'],

            # bold **b**
            [r'\*\*(?P<text>[^*%]+)\*\*', r'<b>\g<text></b>'],

            # cursive *i*
            [r'\*(?P<text>[^*%]+)\*', r'<i>\g<text></i>'],

            # underline
            [r'\[m\](?P<text>.+)\[\/m\]', r'<u>\g<text></u>'],

            # deleted [s]s[/s]
            [r'\[s\](?P<text>.+)\[\/s\]', r'<del>\g<text></del>'],

            # monospace [code]code[/code]
            [r'\[code\](?P<text>.+)\[\/code\]', r'<code>\g<text></code>'],

            #spoiler %%s%%
            [r'\%\%(?P<text>[^*%]+)\%\%',
             r'<span class="spoiler">\g<text></span>'],

            # link to thread >t14
            [r'\&gt;\&gt;t(?P<id>[0-9]+)',
             r'<div class="link_to_content"><a class="link_to_post" href="/thread/\g<id>">&gt;&gt;t\g<id></a><div class="post_quote"></div></div>'],

            # link to post >p88
            [r'\&gt;\&gt;p(?P<id>[0-9]+)',
             r'<div class="link_to_content"><a class="link_to_post" href="/post/\g<id>">&gt;&gt;p\g<id></a><div class="post_quote"></div></div>'],

            # new line
            [r'\n', r'<br>'],

            # link with http-prefix.
            [r'https?:\/\/', r''],

            # link
            [r'\[url=(?P<link>(https?)?:?\/?\/?(www)?\.?[-A-Za-z]+\.[a-z]+(\/[\.\+-_&\?=/A-Za-z0-9]*)?)\]',
             r'<a href="http://\g<link>">\g<link></a>'],

        ]
        for one_markup in markups:
            string = re.sub(one_markup[0], one_markup[1], string)
        return string


class Thread(BasePost):
    post_count = models.IntegerField(default=0)
    update_time = models.DateTimeField('%Y-%m-%d %H:%M:%S', auto_now_add=True)

    # Post attributes.
    topic = models.CharField(max_length=40, blank=False)
    image1 = models.ImageField(upload_to='.', blank=False)
    image2 = models.ImageField(upload_to='.', blank=True)

    def latest_posts(self, count=3):
        posts = Post.objects.filter(thread_id=self).order_by('-id')[:count]  # Get 3 last posts.
        rev_posts = reversed(posts)  # Reverse count.
        return rev_posts

    def __str__(self):
        return '%s' % (self.topic)


class ThreadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ThreadForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Thread
        fields = ['topic', 'text', 'image1', 'image2',
                  'archive', 'board_id', 'user_id']


class Post(BasePost):
    topic = models.CharField(max_length=40, blank=True)
    image1 = models.ImageField(upload_to='.', blank=True)
    image2 = models.ImageField(upload_to='.', blank=True)
    image3 = models.ImageField(upload_to='.', blank=True)
    thread_id = models.ForeignKey(Thread)

    def get_id(self):
        return self.thread_id.id

    def __str__(self):
        return ''.join([self.text[:40], ', ', str(self.date)])


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ['topic', 'text', 'image1', 'image2', 'image3',
                  'archive', 'thread_id', 'board_id', 'user_id']


# Signals

# Callbacks here because save does not always mean new object
@receiver(pre_save, sender=Post)
@receiver(pre_save, sender=Thread)
def pre_save_callback(sender, instance, **kwargs):
    # is it update for something or new object? If it is new, id is None
    if instance.id is None:
        # Topic must be safe
        instance.topic = escape(instance.topic)

        # Markup
        instance.text = instance.markup(instance.text)


@receiver(post_save, sender=Thread)
@receiver(post_save, sender=Post)
def post_save_callback(sender, instance, **kwargs):
    if kwargs['created']:
        # Thumbnail
        instance.make_thumbnail()
