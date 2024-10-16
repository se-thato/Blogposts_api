from rest_framework import serializers
from .models import Post, User
from django.contrib.auth.models import User

class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'author', 'content', 'published_date', 'category']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
       model = User
       fields = ['id','username', 'email', 'password']