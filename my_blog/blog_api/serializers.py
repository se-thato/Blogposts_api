from rest_framework import serializers
from .models import Post, User, Comment, Subscription, Like, Rating
from django.contrib.auth.models import User
from rest_framework.validators import ValidationError


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'author', 'content', 'published_date', 'category']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
       model = User
       fields = ['id','username', 'email', 'password']

    
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'comment', 'published_date', 'upvotes', 'downvotes', 'parent', 'replies']

    def get_replies(self, object):
        if object.replies.exists():
            return CommentSerializer(object.replies.all(), many=True).data
        return []

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'author', 'user', 'published_date' ]
        read_only_fields = ["user", "published_at"]


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=15)
    password = serializers.CharField(write_only=True, max_length=100)
    confirm_password = serializers.CharField(write_only=True, max_length=100)

    class Meta:
        model = User
        fields =['username', 'email', 'password', 'confirm_password']

        #password validation
        def validate(self, data):
            #making sure the password is correct
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({'password': 'Opps!! password do not match please try again..'})
            return data 

        #creating password
        def create(self, validated_data):
            validated_data.pop('confirm_password')
            user = User.objects.create_user(username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password']
            )

            return user