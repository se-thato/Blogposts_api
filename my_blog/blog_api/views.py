from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status,authentication, permissions
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import Post, User, Comment, Subscription, Like
from .serializers import PostSerializer, UserSerializer, RegisterSerializer, CommentSerializer, SubscriptionSerializer, LikeSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.request import Request
import jwt, datetime
from django.core.mail import send_mail

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

    #this view will allow popular/trending posts to be retrieved sorted by calculated
    #show the popularity sum /total
    @api_view(['GET'])
    def popular_posts(request):
        posts = Post.objects.annotate(popularity = F("likes_count") + (2 * F("comments_count")) + (3 * F("shares_count"))).order_by("-popularity")[:10]
        #this will get top 10 trending posts
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


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



#Creating the commnet view section
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

    #nested comments and votings
    #when upvoted
    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        comment = self.get_object()
        comment.upvotes += 1
        comment.save()
        return Response({'status': 'upvoted', 'total_votes': comment.total_votes})
    
    #when downvoted
    @action(detail=True, methods=['post'])
    def downvotes(self, request, pk=None):
        comment = self.get_object()

        comment.donvotes += 1
        comment.save()
        return Response({'status': 'downvoted', 'total_votes': comment.total_votes})

    #notifying users when they are being mentioned in a comment
    def notify_mentions(comment):
        mentions = re.findall(r'@(\w+)', comment.content)
        for username in mentions:
            try:
                user = User.objects.get(username=username)
                send_mail("Hey someone mentioned you in a comment!!", f"{comment.author} mentioned you in a comment: '{comment.content}'",
                          "no-reply@blog.com", [user.email], )
            except User.DoesNotExist:
                pass


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
            
            
    @api_view(['POST'])
    #allowing users to post a reply to an existing comment by specifying the parent comment id
    def reply_to_comment(request, pk):
        try:
            parent_comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response ({'Error': 'Opps Comment Not Found'}, status=404)
        
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, parent=parent_comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=400)

    @api_view(['POST'])
    #allowing comments_count when a comment is being added
    def comment_to_posts(request, pk):
        post = get_object_or_404(Post, pk=pk)
        #since we have comment model this will allow us to see the action on comments
        if request.user in post.comments.all():
            post.comments.remove(request.user)
            post.likes_count -= 1
            action = "comment deleted"
            post.save()
            return Response({"message": f"Ohh No!!{action} from the post"})

        else:
            post.comments.add(request.user)
            post.comments_count += 1
            action = 'commented'
            post.save()
        return Response({"message": f"You have {action} to the post"})
    
    

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


#creating Like and Rating Views 
class LikeListCreate(generics.ListCreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    #only authenticated/logged in users who can see the likes
    permission_classes = [permissions.IsAuthenticated] 
    

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @api_view(['GET', 'POST'])
    def likes_list(request):

        if request.method == 'GET':
            like = Like.objects.all()
            serializer = ListSerializer(like, many=True)
            return Response(serializer.data)
        
        
        if request.method == 'POST':
            serializer = LikeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                post = get_object_or_404(Post, id=post_id)
        if Like.objects.filter(user=request.user, post=post).exists():
            return Response({"message": "Post liked successfully."}, status=status.HTTP_201_CREATED)
        #return Response(serializer.data, status=status.HTTP_201_CREATED)

    @api_view(['POST'])
    def like_posts(request, pk):
        post = get_object_or_404(Post, pk=pk)
        #since we have Like model
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            post.likes_count -= 1
            action = "unliked"
        else:
            post.likes.add(request.user)
            post.likes_count += 1
            action = 'liked'
            post.save()
        return Response({"message": f"You have {action} the post!!"})




    @api_view(['GET', 'PUT', 'DELETE'])
    def likes_detail(request, id):

        try:
            likes = Like.objects.get(pk=id)
        except Like.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        #this will retrieve all the likes
        if request.method == 'GET':
            serializer = LikeSerializer(likes)
            return Response(serializer.data)
        #this will allow the user to change the like
        elif request.method == 'PUT':
            serializer = LikeSerializer(likes, data= request.data)
            if serializer.is_valid():
                serializer.save
        #Allowing the likes to be deleted
        elif request.method == 'DELETE':
            likes.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    #delete option
    def delete(self, request, *args, **kwargs):
        Like.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    #GET, PUT and DELETE
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Like.objects.get(pk=pk, user=self.request.user)
        except Like.DoesNotExist:
            return None

    #GET will get the details of likes based on its primary key(pk)
    def get(self, request, pk):
        likes = self.get_object(pk)
        if likes is None:
            return Response ({"error": "Ohh no!! Liking the post was unsuccessfully."}, status=status.HTTP_404_NOT_FOUND)
            serializer = LikeSerializer(likes)

        return Response(serializer.data, status=status.HTTP_200_OK)


    #PUT will update liking details
    def put(self, request, pk):
        likes = self.get_object(pk)
        if likes is None:
            return Response ({"error": "Liking the post was unsuccessfully."}, status=status.HTTP_404_NOT_FOUND)
            serializer = LikeSerializer(likes, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #DELETE will delete a specific like
    def delete(self, request, pk):
        likes = self.get_object(pk)
        if likes is None:
            return Response ({"error": "Ohh no!! Like not found."}, status=status.HTTP_404_NOT_FOUND)
            likes.delete()
        return Response ({"message": "Like is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        Like.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



#creating subscription view section
class SubscriptionListCreate(generics.ListCreateAPIView):
    #GET(get all the the subscription) POST(create new subscription)

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    #only authenticated/logged in users who can see the subscriber
    permission_classes = [permissions.IsAuthenticated] 

    #GET will display list of all subscriptions for loggeg in users
    def get(self, request):
        subscriptions=Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #POST will allow users to create new subscription
    def post(self, request):
        SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            #save subscription for authenticated user or logged in user
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionDetailView(generics.ListCreateAPIView):
    #GET, PUT and DELETE
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Subscription.objects.get(pk=pk, user=self.request.user)
        except Subscription.DoesNotExist:
            return None

    #GET will get the details of a subscription based on its primary key(pk)
    def get(self, request, pk):
        subscription = self.get_object(pk)
        if subscription is None:
            return Response ({"error": "Ohh no!! Subscription not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = SubscriptionSerializer(subscription)

        return Response(serializer.data, status=status.HTTP_200_OK)


    #PUT will update a subscription details
    def put(self, request, pk):
        subscription = self.get_object(pk)
        if subscription is None:
            return Response ({"error": "Ohh no!! Subscription not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = SubscriptionSerializer(subscription, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #DELETE will delete a specific subscription
    def delete(self, request, pk):
        subscription = self.get_object(pk)
        if subscription is None:
            return Response ({"error": "Ohh no!! Subscription not found."}, status=status.HTTP_404_NOT_FOUND)
            subscription.delete()
        return Response ({"message": "Subscription is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        Subscription.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



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
        return Response({'message': "You've Been Registered Successfully!!"}, status=status.HTTP_201_CREATED)

    @api_view(['POST'])
    def register(request):
        if request.method == 'POST':
            return Response({'message': "You've Been Registered Successfully!!"}, status=status.HTTP_201_CREATED)


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
        



        
