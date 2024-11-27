from django.shortcuts import render
from rest_framework import generics, status,authentication, permissions
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import Post, User, Comment
from .serializers import PostSerializer, UserSerializer, RegisterSerializer, CommentSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.request import Request
import jwt, datetime

class PostListCreate(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    #creating search feature
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content', 'author__username', 'category']
    #creating pagination
    pagination_class = PageNumberPagination


    #creating an endpoint
    @api_view(['GET', 'POST'])
    def post_list(request):

        #get all the available blogposts
        #serialize them
        #return json 
        if request.method == 'GET':
            post = Post.objects.all()
            serializer = PostSerializer(post, many=True)
            return Response(serializer.data)
        
        
        if request.method == 'POST':
            serializer = PostSerializer(data=request.data)
            #check if the data sent is  valid
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)



    @api_view(['GET', 'PUT', 'DELETE'])
    def post_detail(request, id):

        try:
            post = Post.objects.get(pk=id)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = PostSerializer(post)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = PostSerializer(post, data= request.data)
            if serializer.is_valid():
                serializer.save

        elif request.method == 'DELETE':
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    #creating the delete button on my blogpost list create page
    def delete(self, request, *args, **kwargs):
        Post.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'pk'

#Creating the commnet section
class CommentListCreate(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    search_fields = ['title', 'post', 'author__username', 'comment']
    #only authenticated/logged in users who can see the comment
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
    #creating pagination
    pagination_class = PageNumberPagination
    

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @api_view(['GET', 'POST'])
    def comment_list(request):

        #get all the available blogposts
        #serialize them
        #return json 
        if request.method == 'GET':
            comment = Comment.objects.all()
            serializer = CommentSerializer(comment, many=True)
            return Response(serializer.data)
        
        
        if request.method == 'POST':
            serializer = CommentSerializer(data=request.data)
            #checking the if the data is valid
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)


    @api_view(['GET', 'PUT', 'DELETE'])
    def comments_detail(request, id):

        try:
            comment = Comment.objects.get(pk=id)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        #this will retrieve the comments
        if request.method == 'GET':
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        #this will allow the user to update their comment
        elif request.method == 'PUT':
            serializer = CommentSerializer(comment, data= request.data)
            if serializer.is_valid():
                serializer.save
        #Allowing the comments to be deleted
        elif request.method == 'DELETE':
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    #delete option
    def delete(self, request, *args, **kwargs):
        Comment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
            
class CommentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'pk'


class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):
        User.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()                                     
    serializer_class = UserSerializer   
    lookup_field = 'pk'                       




#setting up authentication

class ListUsers(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })





#register a user
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            
            return Response({'message': "You've Been Registered Successfully!!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user= User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password():
            raise AuthenticationFailded('incorect password')
        
        payload = {
            'id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()

        }

        token = jwt.encode(payload, 'secret', algorithm= 'HS256').decode('utf-8')

        return Response({
            'jwt': token
        })
        



        
