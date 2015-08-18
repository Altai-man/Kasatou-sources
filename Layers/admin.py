"""Admin file for Kasatou."""
from django.contrib import admin
from Layers.models import Board, Thread, Post, User, Invite

admin.site.register(Board)
admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(User)
admin.site.register(Invite)
