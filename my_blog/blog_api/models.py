from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser


class Post(models.Model):
    title = models.CharField(max_length= 100)
    #author = models.CharField(max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    category = models.TextField()

    def __str__(self): 
        return self.title   


#creating a comment section
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        #when someone comment we'll be able to see the post, title and their name
        return '%s - %s' % (self.post.title, self.author)
    


#creating the subscription section 
class Subscription(models.Model):
    pass
"""
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=15, unique=True)
    password = models.CharField(max_length=100)
    
    def __str__(self): 
        return self.username
    
"""

#creating an authentication(generatin a token when a user create an account)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)






#creating custom user manager
class CustomerUserManager(BaseUserManager):
    def create_user(self,email, password, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email =self.normalize_email(email)
        user =self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

"""
        user=self.model(
            email =email,
            **extra_fields
        )
        #seeting a password 
        user.set_password(password)

        user.save()

        return user
 
"""


#method for creating a superuser
def create_superuser(self, email, password,**extra_fields):
    extra_fields.setdefault("is_staff",True)
    extra_fields.setdefault("is_superuser",True)

    if extra_fields.get("is_staff") is not True:
        raise ValueError("Superuser has to have is_staff being True")

    
    if extra_fields.get("is_superuser") is not True:
        raise ValueError("Superuser has to have is_superuser being True")


    return self.create_user(email=email, password=password,**extra_fields)



class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=15, unique=True)
    password = models.CharField(max_length=100)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects=CustomerUserManager()

    groups = models.ManyToManyField('auth.Group', related_name = 'custom_user_groups')

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name= 'custom_user_permissions'
    )

    def __str__(self):
        return self.username