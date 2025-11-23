from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user

    def get_user_profile(self):
        try:
            user_obj = User.objects.get(username=self.user)
            return Profile.objects.get(user=user_obj)
        except:
            return None

class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user


# core/models.py (Notification model excerpt)

class Notification(models.Model):
    NOTIF_TYPES = (
        ('like', 'Like'),
        ('follow', 'Follow'),
        ('post', 'Post'),
        ('comment', 'Comment'),   # <-- added comment type
    )

    to_user = models.CharField(max_length=150)
    actor = models.CharField(max_length=150)
    verb = models.CharField(max_length=255)
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES)

    post_id = models.CharField(max_length=200, blank=True, null=True)
    url = models.CharField(max_length=500, blank=True)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return f"{self.actor} {self.verb} → {self.to_user}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.CharField(max_length=150)           # username of commenter
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)  # oldest first; use '-timestamp' if you prefer newest first

    def __str__(self):
        return f"{self.user} on {self.post.id}: {self.body[:30]}"
    

class Block(models.Model):
    """
    Records that `blocker` has blocked `blocked`.
    Storing usernames (like your other models) to match your project style.
    """
    blocker = models.CharField(max_length=150)   # username who blocks
    blocked = models.CharField(max_length=150)   # username who is blocked
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')
        ordering = ('-timestamp',)

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"