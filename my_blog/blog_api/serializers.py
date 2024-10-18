from rest_framework import serializers
from .models import Post, User
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

   