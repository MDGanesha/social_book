from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import get_object_or_404
from django.db.models import Q
from itertools import chain
import random

from .models import Profile, Post, LikePost, FollowersCount, Notification, Comment, Block
from .serializers import (
    UserSerializer, ProfileSerializer, PostSerializer, LikePostSerializer,
    FollowersCountSerializer, CommentSerializer, NotificationSerializer, BlockSerializer
)
from .utils import create_notification


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Profile model.
    list: Get all profiles
    retrieve: Get a specific profile
    update: Update own profile
    partial_update: Partially update own profile
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Profile.objects.all()
        username = self.request.query_params.get('username', None)
        if username:
            queryset = queryset.filter(user__username__icontains=username)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Update current user's profile"""
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Post model.
    list: Get all posts (filtered by user if provided)
    retrieve: Get a specific post
    create: Create a new post
    update: Update own post
    destroy: Delete own post
    """
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-created_at')
        username = self.request.query_params.get('user', None)
        if username:
            queryset = queryset.filter(user=username)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.username)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        """Like or unlike a post"""
        post = self.get_object()
        username = request.user.username
        like_filter = LikePost.objects.filter(post_id=str(post.id), username=username).first()

        if like_filter is None:
            # Like the post
            LikePost.objects.create(post_id=str(post.id), username=username)
            post.no_of_likes += 1
            post.save()

            # Create notification
            if post.user != username:
                create_notification(
                    to_username=post.user,
                    actor_username=username,
                    verb="liked your post",
                    notif_type="like",
                    post_id=str(post.id),
                    url=f"/profile/{post.user}"
                )

            return Response({'status': 'liked', 'likes': post.no_of_likes}, status=status.HTTP_201_CREATED)
        else:
            # Unlike the post
            like_filter.delete()
            post.no_of_likes -= 1
            post.save()
            return Response({'status': 'unliked', 'likes': post.no_of_likes})

    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Get feed posts (posts from users you follow)"""
        me = request.user.username

        # Get users I follow
        user_following = FollowersCount.objects.filter(follower=me)
        following_usernames = [f.user for f in user_following]

        # Get blocks
        blocked_by_me_qs = Block.objects.filter(blocker=me).values_list('blocked', flat=True)
        blocked_me_qs = Block.objects.filter(blocked=me).values_list('blocker', flat=True)
        blocked_by_me = set(blocked_by_me_qs)
        blocked_me = set(blocked_me_qs)

        # Build feed
        feed = []
        for username in following_usernames:
            if username in blocked_by_me or username in blocked_me:
                continue
            qs = Post.objects.filter(user=username)
            feed.append(qs)
        feed_list = list(chain(*feed))
        feed_list.sort(key=lambda x: x.created_at, reverse=True)

        serializer = self.get_serializer(feed_list, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get user suggestions"""
        me = request.user.username
        all_users = User.objects.exclude(username=me)

        # Get users I follow
        user_following = FollowersCount.objects.filter(follower=me)
        following_usernames = set([f.user for f in user_following])

        # Get blocks
        blocked_by_me_qs = Block.objects.filter(blocker=me).values_list('blocked', flat=True)
        blocked_me_qs = Block.objects.filter(blocked=me).values_list('blocker', flat=True)
        blocked_by_me = set(blocked_by_me_qs)
        blocked_me = set(blocked_me_qs)

        exclude_usernames = following_usernames.union({me}).union(blocked_by_me).union(blocked_me)
        suggestions = [u for u in all_users if u.username not in exclude_usernames]
        random.shuffle(suggestions)

        username_profile_list = []
        for u in suggestions[:10]:
            try:
                profile = Profile.objects.get(id_user=u.id)
                username_profile_list.append(profile)
            except:
                pass

        serializer = ProfileSerializer(username_profile_list[:4], many=True, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment model.
    list: Get all comments for a post
    create: Create a new comment
    destroy: Delete own comment
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Comment.objects.all()
        post_id = self.request.query_params.get('post', None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset.order_by('timestamp')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.username)
        post = serializer.instance.post
        # Create notification
        if post.user != self.request.user.username:
            create_notification(
                to_username=post.user,
                actor_username=self.request.user.username,
                verb="commented on your post",
                notif_type="comment",
                post_id=str(post.id),
                url=f"/profile/{post.user}"
            )


class FollowersCountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FollowersCount model.
    list: Get followers/following
    create: Follow a user
    destroy: Unfollow a user
    """
    queryset = FollowersCount.objects.all()
    serializer_class = FollowersCountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FollowersCount.objects.all()
        user = self.request.query_params.get('user', None)
        follower = self.request.query_params.get('follower', None)
        if user:
            queryset = queryset.filter(user=user)
        if follower:
            queryset = queryset.filter(follower=follower)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Follow or unfollow a user"""
        follower = request.user.username
        user = request.data.get('user')

        if not user:
            return Response({'error': 'user field is required'}, status=status.HTTP_400_BAD_REQUEST)

        if follower == user:
            return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        follow_obj = FollowersCount.objects.filter(follower=follower, user=user).first()

        if follow_obj:
            follow_obj.delete()
            return Response({'status': 'unfollowed'})
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            if follower != user:
                create_notification(
                    to_username=user,
                    actor_username=follower,
                    verb="started following you",
                    notif_type="follow",
                    url=f"/profile/{follower}"
                )
            serializer = self.get_serializer(new_follower)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def followers(self, request):
        """Get followers of a user"""
        username = request.query_params.get('user', request.user.username)
        followers = FollowersCount.objects.filter(user=username)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def following(self, request):
        """Get users that a user is following"""
        username = request.query_params.get('user', request.user.username)
        following = FollowersCount.objects.filter(follower=username)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Notification model (read-only).
    list: Get all notifications for current user
    retrieve: Get a specific notification
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(to_user=self.request.user.username).order_by('-timestamp')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        if notification.to_user != request.user.username:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        notification.read = True
        notification.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        Notification.objects.filter(to_user=request.user.username, read=False).update(read=True)
        return Response({'status': 'all marked as read'})


class BlockViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Block model.
    list: Get blocked users
    create: Block a user
    destroy: Unblock a user
    """
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Block.objects.filter(blocker=self.request.user.username)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Block or unblock a user"""
        blocker = request.user.username
        blocked = request.data.get('blocked')

        if not blocked:
            return Response({'error': 'blocked field is required'}, status=status.HTTP_400_BAD_REQUEST)

        if blocked == blocker:
            return Response({'error': 'Cannot block yourself'}, status=status.HTTP_400_BAD_REQUEST)

        block_obj = Block.objects.filter(blocker=blocker, blocked=blocked).first()

        if block_obj:
            block_obj.delete()
            # Optionally restore follow relationships
            FollowersCount.objects.filter(follower=blocker, user=blocked).delete()
            FollowersCount.objects.filter(follower=blocked, user=blocker).delete()
            return Response({'status': 'unblocked'})
        else:
            block_obj = Block.objects.create(blocker=blocker, blocked=blocked)
            # Remove follow relationships
            FollowersCount.objects.filter(follower=blocker, user=blocked).delete()
            FollowersCount.objects.filter(follower=blocked, user=blocker).delete()
            serializer = self.get_serializer(block_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# Authentication views
@api_view(['POST'])
@permission_classes([AllowAny])
def api_signup(request):
    """User registration"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    password2 = request.data.get('password2')

    if not all([username, email, password, password2]):
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    if password != password2:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already taken'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    # Create profile
    new_profile = Profile.objects.create(user=user, id_user=user.id)
    new_profile.save()

    # Log user in
    auth.login(request, user)

    return Response({
        'message': 'User created successfully',
        'user': UserSerializer(user).data,
        'profile': ProfileSerializer(new_profile, context={'request': request}).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """User login"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = auth.authenticate(username=username, password=password)

    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    auth.login(request, user)

    try:
        profile = Profile.objects.get(user=user)
        profile_data = ProfileSerializer(profile, context={'request': request}).data
    except Profile.DoesNotExist:
        profile_data = None

    return Response({
        'message': 'Login successful',
        'user': UserSerializer(user).data,
        'profile': profile_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """User logout"""
    auth.logout(request)
    return Response({'message': 'Logout successful'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_info(request):
    """Get current user information"""
    try:
        profile = Profile.objects.get(user=request.user)
        profile_data = ProfileSerializer(profile, context={'request': request}).data
    except Profile.DoesNotExist:
        profile_data = None

    return Response({
        'user': UserSerializer(request.user).data,
        'profile': profile_data
    })

