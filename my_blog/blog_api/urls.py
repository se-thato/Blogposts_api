from django.urls import path
from . import views
from blog_api.views import ListUsers, CustomAuthToken
from django.contrib.auth.views import LoginView
#from .views import reply_to_comment


urlpatterns = [
    path('posts/', views.PostListCreate.as_view(), name='post-create'),
    path('posts/<int:pk>/', views.PostRetrieveUpdateDestroy.as_view(), name= 'update'),
    #User section
    path('user/', views.UserListCreate.as_view(), name='user'),
    path('user/<int:pk>/', views.UserRetrieveUpdateDestroy.as_view(), name= 'update-user'),
    #comments section
    path('comments/', views.CommentListCreate.as_view(), name= 'comments'),
    path('comments/<int:pk>/', views.CommentRetrieveUpdateDestroy.as_view(), name= 'comments_update'),
    #path('comments_reply/<int:pk>/', views.reply_to_comment.as_view(), name= 'reply_to_comment' ),
    #subscription section
    path('subscriptions/', views.SubscriptionListCreate.as_view(), name = "subscriptions_list"),
    path('subscriptions/<int:pk>/', views.SubscriptionDetailView.as_view(), name = "subscriptions_details"),
    #like and rating section 
    path('likes/', views.LikeListCreate.as_view(), name = "liked_posts"),
    path('likes/<int:pk>/', views.LikeRetrieveUpdateDestroy.as_view(), name = "likes_delete"),

    path("register/", views.RegisterView.as_view(), name="register"),
    path('login/', views.LoginView.as_view(), name='login'),
    

    path('api/users/', ListUsers.as_view()),
    path('api/token/auth/', CustomAuthToken.as_view()),
]