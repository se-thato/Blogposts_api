from django.urls import path
from . import views
from blog_api.views import ListUsers, CustomAuthToken


urlpatterns = [
    path('posts/', views.PostListCreate.as_view(), name='post-create'),
    path('posts/<int:pk>/', views.PostRetrieveUpdateDestroy.as_view(), name= 'update'),
    path('user/', views.UserListCreate.as_view(), name='user'),
    path('user/<int:pk>/', views.UserRetrieveUpdateDestroy.as_view(), name= 'update-user'),
    
    path('api/users/', ListUsers.as_view()),
    path('api/token/auth/', CustomAuthToken.as_view()),
]