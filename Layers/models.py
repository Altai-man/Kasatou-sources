#! -*- coding: utf-8 -*-
# Pyhon
import os
from PIL import Image
import re

# Django
from django.db import models
from django.contrib.auth.models import User


class SearchManager(models.Manager):
    # Search func.
    def search(self, search_text):
        # Making search text safe
        search_text = escape(search_text)
        query = self.filter(text__icontains=search_text)

        return query


class User(models.Model):

    theme = models.CharField(max_length=10)
    name = models.CharField(max_length=14, default='Anonymous')
    thread_per_page = models.IntegerField(default=8)
    rank = models.IntegerField(default=1)

    def __str__(self):
        return '%s, with %s rank.' % (self.name, self.rank)


class Board(models.Model):
    board_name = models.CharField(max_length=3)
    thread_max_post = models.IntegerField(default=500)

    def get_board_view(self):
        threads = Thread.objects.filter(board_id=self).order_by('-update_time')
        return [dict(thread=th, posts=th.latest_posts()) for th in threads]

    def __str__(self):
        return '/%s/' % (self.board_name)


class Thread(models.Model):
    post_count = models.IntegerField(default=0)
    topic = models.CharField(max_length=40)
    update_time = models.DateTimeField('%Y-%m-%d %H:%M:%S', auto_now_add=True)
    board_id = models.ForeignKey(Board)

    def latest_posts(self, count=5):
        posts = reversed(Post.objects.filter(thread_id=self).order_by('-id')[:count])

    def save(self, *args, **kwargs):
        super(Thread, self).save(*args, **kwargs)

    def __str__(self):
        return ''.join()


class Post(models.Model):
    text = models.TextField(max_length=5000, blank=True)
    date = models.DateTimeField('%Y-%m-%d %H:%M:%S', auto_now_add=True)
    image1 = models.ImageField(upload_to='.', blank=True)
    image2 = models.ImageField(upload_to='.', blank=True)
    image3 = models.ImageField(upload_to='.', blank=True)
    archive = models.FileField(upload_to='documents', blank=True)
    thread_id = models.ForeignKey(Thread)
    board_id = models.ForeignKey('board')

    def make_thumbnail(self):
        if self.image1:
            ratio = min(settings.PIC_SIZE/self.image1.height, settings.PIC_SIZE/self.image1.width)
            thumbnail = Image.open(self.image1.path)
            thumbnail.thumbnail((int(self.image1.width*ratio), int(self.image1.height*ratio)), Image.ANTIALIAS)
            thumbnail.save(''.join([settings.MEDIA_ROOT, '/thumbnails/', self.image1.name]), thumbnail.format)
        if self.image2:
            ratio = min(settings.PIC_SIZE/self.image2.height, settings.PIC_SIZE/self.image2.width)
            thumbnail = Image.open(self.image2.path)
            thumbnail.thumbnail((int(self.image2.width*ratio), int(self.image2.height*ratio)), Image.ANTIALIAS)
            thumbnail.save(''.join([settings.MEDIA_ROOT, '/thumbnails/', self.image2.name]), thumbnail.format)
        if self.image3:
            ratio = min(settings.PIC_SIZE/self.image3.height, settings.PIC_SIZE/self.image3.width)
            thumbnail = Image.open(self.image3.path)
            thumbnail.thumbnail((int(self.image3.width*ratio), int(self.image3.height*ratio)), Image.ANTIALIAS)
            thumbnail.save(''.join([settings.MEDIA_ROOT, '/thumbnails/', self.image3.name]), thumbnail.format)
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
             r'<span class="quote">\g<text></span>'],

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
            # [r'https?:\/\/', r''],
            # TODO: Delete this latter after text testing.

            # link||text -> <link>text</link>
            [r'(?P<link>https?://[^\s<>"]+|www\.[^\s<>"]+)\|\|(?P<text>\w+)',
             r'<a href="http://\g<link>">\g<text></a>'],
        ]

        for one_markup in markups:
            string = re.sub(one_markup[0], one_markup[1], string)
        return string

    # Add search tool.
    objects = SearchManager()

    def __str__(self):
        return ''.join([self.board_id, ': ', self.text[:40], ', ', str(self.date)])
