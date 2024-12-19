from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length= 100)
    #author = models.CharField(max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length = 50, default='Tech')

    def __str__(self): 
        return self.title   


#creating a comment section
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    #adding nested comments,mentions and voting
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    upvotes = models.IntegerField(default=0)
    downvotes =models.IntegerField(default=0)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        #when someone comment we'll be able to see the post, title and their name
        return '%s - %s' % (self.post.title, self.author)
    
    @property
    def total_votes(self):
        return self.upvotes - self.downvotes


#Creating the like section 
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name= "likes", on_delete=models.CASCADE)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"


#Rating section 
class Rating(models.Model):
    post = models.ForeignKey(Post, related_name= "ratings", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #rating score on a scale
    score = models.IntegerField()
    published_at = models.DateTimeField(auto_now_add=True)




#creating the subscription section 
User = get_user_model

class Subscription(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name= "subscription")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name = "subscribers")
    published_date = models.DateTimeField(auto_now_add= True)

    class Meta:
        #preventing repeated subsciptions
        unique_together = ("user", "author")

    def __str__(self):
        return f"{self.user} subscribes to {self.author}"
 

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