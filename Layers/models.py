from django.db import models
from django.contrib.auth.models import User


class SearchManager(models.Manager):
    # Search func.
    def search(self, search_text, search_place, board):
        # Making search text safe
        search_text = escape(search_text)
        query = self.filter(text__icontains=search_text)

        return query


class User(models.Model):
    theme = models.CharField(max_length=10)
    name = models.CharField(max_length=14, default='Anonymous')
    thread_per_page = models.IntegerField(default=8)
    rank = models.IntegerField(default=1)


class Board(models.Model):
    board_name = models.CharField(max_length=3)
    thread_max_post = models.IntegerField(default=500)


class Thread(models.Model):
    post_count = models.IntegerField(default=0)
    topic = models.CharField(max_length=40)
    update_time = models.DateTimeField('%Y-%m-%d %H:%M:%S', auto_now_add=True)
    board_id = models.ForeignKey(Board)


class Post(models.Model):
    text = models.TextField(max_length=5000, blank=True)
    date = models.DateTimeField('%Y-%m-%d %H:%M:%S', auto_now_add=True)
    image1 = models.ImageField(upload_to='.', blank=True)
    image2 = models.ImageField(upload_to='.', blank=True)
    image3 = models.ImageField(upload_to='.', blank=True)
    archive = models.FileField(upload_to='documents', blank=True)
    thread_id = models.ForeignKey(Thread)
