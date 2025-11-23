from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Post, LikePost, FollowersCount, Notification, Comment, Block


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    profileimg_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'username', 'id_user', 'bio', 'profileimg', 'profileimg_url', 'location']
        read_only_fields = ['id', 'user', 'id_user']

    def get_profileimg_url(self, obj):
        if obj.profileimg:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profileimg.url)
            return obj.profileimg.url
        return None


class PostSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'user_profile', 'image', 'image_url', 'caption', 'created_at', 
                  'no_of_likes', 'is_liked', 'comments_count']
        read_only_fields = ['id', 'created_at', 'no_of_likes']

    def get_user_profile(self, obj):
        profile = obj.get_user_profile()
        if profile:
            return ProfileSerializer(profile, context=self.context).data
        return None

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LikePost.objects.filter(post_id=str(obj.id), username=request.user.username).exists()
        return False

    def get_comments_count(self, obj):
        return obj.comments.count()


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikePost
        fields = ['id', 'post_id', 'username']
        read_only_fields = ['id']


class FollowersCountSerializer(serializers.ModelSerializer):
    follower_profile = serializers.SerializerMethodField()
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = FollowersCount
        fields = ['id', 'follower', 'user', 'follower_profile', 'user_profile']
        read_only_fields = ['id']

    def get_follower_profile(self, obj):
        try:
            user = User.objects.get(username=obj.follower)
            profile = Profile.objects.get(user=user)
            return ProfileSerializer(profile, context=self.context).data
        except:
            return None

    def get_user_profile(self, obj):
        try:
            user = User.objects.get(username=obj.user)
            profile = Profile.objects.get(user=user)
            return ProfileSerializer(profile, context=self.context).data
        except:
            return None


class CommentSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'user_profile', 'body', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    def get_user_profile(self, obj):
        try:
            user = User.objects.get(username=obj.user)
            profile = Profile.objects.get(user=user)
            return ProfileSerializer(profile, context=self.context).data
        except:
            return None


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'to_user', 'actor', 'verb', 'notif_type', 'post_id', 'url', 'read', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class BlockSerializer(serializers.ModelSerializer):
    blocked_profile = serializers.SerializerMethodField()
    blocker_profile = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = ['id', 'blocker', 'blocked', 'blocker_profile', 'blocked_profile', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    def get_blocked_profile(self, obj):
        try:
            user = User.objects.get(username=obj.blocked)
            profile = Profile.objects.get(user=user)
            return ProfileSerializer(profile, context=self.context).data
        except:
            return None

    def get_blocker_profile(self, obj):
        try:
            user = User.objects.get(username=obj.blocker)
            profile = Profile.objects.get(user=user)
            return ProfileSerializer(profile, context=self.context).data
        except:
            return None

