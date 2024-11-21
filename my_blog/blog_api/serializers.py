from rest_framework import serializers
from .models import Post, User, Comment
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
    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'comment', 'published_date' ]


"""
class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=15)
    password = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        #hiding the password
        extra_kwargs = {
            'password': {'write_only': True}
        }

    #creating validation for the user
    def validate(self,attrs):

        email_exists = User.objects.filter(email=attrs['email']).exists

        if email_exists:
            raise ValidationError("Email already exists")
        
        return super().validate(attrs)
    


    def create(self, validated_data):
        password =validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
            instance.save()

            return instance

        user =super().create(validated_data)

        user.set_password(password)

        user.save()

        return user

"""

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