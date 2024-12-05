from django.contrib import admin
from .models import Post, Comment, Subscription, Like


# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Subscription)
admin.site.register(Like)
