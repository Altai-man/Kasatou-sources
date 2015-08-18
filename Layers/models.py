#! -*- coding: utf-8 -*-
"""Description of Kasatou models."""
from PIL import Image
import re
import random
import string

# Django
from django.db import models
from django.utils.html import escape
from django.contrib.auth.models import (AbstractBaseUser,
                                        PermissionsMixin, BaseUserManager)
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from Kasatou.settings import PIC_SIZE, MEDIA_ROOT


# Method for files.
def content_file_name(instance, filename):
    """Create new filename for uploads."""
    # At first we add a few symbols of date.
    name = '/'.join([str(instance.date)[:9]])
    if "jpeg" in filename[-4:]:
        name = name + filename[-5:]
        # Because in '.jpeg' is more that 4 symbols.
    else:
        name = name + filename[-4:]  # Here is jpg, png and so.

    return name


class SearchManager(models.Manager):
    def search(self, search_text):
        """Provide search for posts."""
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

    email = models.EmailField('Email', max_length=255, unique=True)
    theme = models.CharField(max_length=10, default="Light")
    date_joined = models.DateTimeField('Date joined', default=timezone.now)
    invites_count = models.IntegerField(default=3)

    is_admin = models.BooleanField('Admin status', default=False)
    is_active = models.BooleanField('Active', default=True)

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Anonymous'
        verbose_name_plural = 'Anonymouses'

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True if self.is_admin else False

    def has_module_perms(self, app_label):
        return True if self.is_admin else False

    @property
    def is_staff(self):
        return self.is_admin


class Invite(models.Model):
    is_active = models.BooleanField(default=True)
    code = models.CharField(max_length=32)
    sender = models.ForeignKey(User)

    def generate_code(self):
        self.code = ''.join(random.choice(string.ascii_letters + string.digits)
                            for x in range(32))

    @staticmethod
    def check_invite(code):
        try:
            curr_invite = Invite.objects.get(code=code)
        except Invite.DoesNotExist:
            curr_invite = None

        if curr_invite is not None:
            curr_invite.is_active = False
            return True
        else:
            return False

    def __str__(self):
        return 'Invite №%s.' % self.id


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
    text = models.TextField(max_length=5000, blank=True)
    date = models.DateTimeField('%Y-%m-%d %H:%M:%S', auto_now_add=True)
    archive = models.FileField(upload_to='documents', blank=True)
    board_id = models.ForeignKey(Board)
    user_id = models.ForeignKey(User)

    def thumb(self, image):
        ratio = min(PIC_SIZE/image.height,
                    PIC_SIZE/image.width)
        thumbnail = Image.open(image.path)
        thumbnail.thumbnail((int(image.width*ratio),
                             int(image.height*ratio)),
                            Image.ANTIALIAS)
        path = ''.join([MEDIA_ROOT, '/thumbnails/', image.name])
        thumbnail.save(path, thumbnail.format)

    def make_thumbnail(self):
        if self.image1:
            self.thumb(self.image1)
        if self.image2:
            self.thumb(self.image1)
        return True

    @staticmethod
    def unmarkup(raw_string):
        unmarkups = [
            # link like url
            [r'<a href="(?P<link>.*?)">.*?</a>',
             r'[url=\g<link>]'],

            # link to post style
            [r'</?div.*?>',
             r''],

            # link to post url
            [r'</?a( class="link_to_post".+?)?>',
             r''],

            # bold **b**
            [r'<b>(?P<text>.*?)</b>',
             r'**\g<text>**'],

            # cursive *i*
            [r'<i>(?P<text>.*?)</i>',
             r'*\g<text>*'],

            # underline
            [r'<u>(?P<text>.*?)</u>',
             r'[m]\g<text>[/m]'],

            # deleted [s]s[/s]
            [r'<del>(?P<text>.*?)</del>',
             r'[s]\g<text>[/s]'],

            # monospace [code]code[/code]
            [r'<code>(?P<text>.*?)</code>',
             r'[code]\g<text>[/code]'],

            # spoiler %%s%%
            [r'<span class="spoiler">(?P<text>(.|\n)*?)</span>',
             r'%%\g<text>%%'],

            # censored [cens]censored[/cens]
            [r'<span class="censored">(?P<text>.*?)</span>',
             r'[cens]\g<text>[/cens]'],

            [r'<span class="post_quote">(?P<text>(.|\n)*?)</span>',
             r'\g<text>']
        ]
        for one_markup in unmarkups:
            raw_string = re.sub(one_markup[0],
                                one_markup[1],
                                raw_string,
                                re.DOTALL)
        raw_string = raw_string.replace("<br>", '\n')
        return raw_string

    @staticmethod
    def markup(raw_string):
        """ Makes markup for post and thread text. Strings will be safe. """
        markups = [
            # bold **b**
            [r'\*\*(?P<text>[^*%]+)\*\*',
             r'<b>\g<text></b>'],

            # cursive *i*
            [r'\*(?P<text>[^*%]+)\*',
             r'<i>\g<text></i>'],

            # underline
            [r'\[m\](?P<text>.+)\[\/m\]',
             r'<u>\g<text></u>'],

            # deleted [s]s[/s]
            [r'\[s\](?P<text>.+?)\[\/s\]',
             r'<del>\g<text></del>'],

            # monospace [code]code[/code]
            [r'\[code\](?P<text>.+)\[\/code\]',
             r'<code>\g<text></code>'],

            # spoiler %%s%%
            [r'%%(?P<text>(.|\n)*?)%%',
             r'<span class="spoiler">\g<text></span>'],

            # censored [cens]censored[/cens]
            [r'\[cens\](?P<text>.*?)\[/cens\]',
             r'<span class="censored">\g<text></span>'],

            # link to thread >t14
            [r'>>t(?P<id>[0-9]+)',
             r'<div class="link_to_content"><a class="link_to_post">&gt;&gt;t\g<id></a><div class="post_quote"></div></div>'],

            # link to post >p88
            [r'>>p(?P<id>[0-9]+)',
             r'<div class="link_to_content"><a class="link_to_post" href="#post_\g<id>">&gt;&gt;p\g<id></a><div class="post_quote"></div></div>'],

            # link
            [r'\[url=(?P<link>.*?)\]',
             r'<a href="\g<link>">\g<link></a>'],
        ]
        for one_markup in markups:
            raw_string = re.sub(one_markup[0],
                                one_markup[1],
                                raw_string,
                                re.DOTALL)

        # quotes
        quotes = [r'^(?P<text>(?<!(>))>.+?)\Z',
                  r'<span class="post_quote">\g<text></span>']
        ready = raw_string.split("\r\n")
        raw_string = '\r\n'.join([
            re.sub(quotes[0], quotes[1], x) for x in ready])

        #  We fix bug with newline characters here:
        raw_string = raw_string.replace('\n', '<br>')
        return raw_string


class Thread(BasePost):
    """Thread object."""
    post_count = models.IntegerField(default=0)
    update_time = models.DateTimeField('%Y-%m-%d %H:%M:%S', auto_now_add=True)

    # Post attributes.
    topic = models.CharField(max_length=40, blank=False)
    image1 = models.ImageField(upload_to=content_file_name, blank=False)
    image2 = models.ImageField(upload_to=content_file_name, blank=True)

    def latest_posts(self, count=3):
        """Return N last posts(default is 3)."""
        # Get 3 last posts.
        posts = Post.objects.filter(thread_id=self).order_by('-id')[:count]
        rev_posts = reversed(posts)  # Reverse count.
        return rev_posts

    def __str__(self):
        return '%s' % self.topic


class Post(BasePost):
    """Post object."""
    objects = SearchManager()

    topic = models.CharField(max_length=40, blank=True)
    image1 = models.ImageField(upload_to=content_file_name, blank=True)
    image2 = models.ImageField(upload_to=content_file_name, blank=True)
    image3 = models.ImageField(upload_to=content_file_name, blank=True)
    thread_id = models.ForeignKey(Thread)

    # Overload base method, because post has three pictures, not two.
    def make_thumbnail(self):
        """Make thumbnail for images if any."""
        if self.image1:
            self.thumb(self.image1)
        if self.image2:
            self.thumb(self.image2)
        if self.image3:
            self.thumb(self.image3)
        return True

    def get_thread_id(self):
        """Simply returns id of thread which post belongs to."""
        return self.thread_id.id

    def __str__(self):
        return ''.join(['Post № ', str(self.id),
                        ' at ',
                        str(self.date.strftime('%Y-%m-%d'))])


# Signals
# Callbacks here because save does not always mean new object
@receiver(pre_save, sender=Post)
@receiver(pre_save, sender=Thread)
def pre_save_callback(sender, instance, **kwargs):
    """Escape topic of post and apply markup to text."""
    # is it update for something or new object? If it is new, id is None
    if instance.id is None:
        # Topic must be safe
        instance.topic = escape(instance.topic)
        # Markup
        instance.text = instance.markup(instance.text)


@receiver(post_save, sender=Thread)
@receiver(post_save, sender=Post)
def post_save_callback(sender, instance, **kwargs):
    """Make thumbnail if post was edited from admin panel."""
    instance.make_thumbnail()
