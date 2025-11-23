from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth 
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount, Block
from itertools import chain
import random
from .utils import create_notification
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification
from django.shortcuts import render, redirect, get_object_or_404


# Create your views here.


@login_required(login_url='signin')
def index(request):
    me = request.user.username
    user_object = User.objects.get(username=me)
    user_profile = Profile.objects.get(user=user_object)

    # find users I follow
    user_following = FollowersCount.objects.filter(follower=me)
    following_usernames = [f.user for f in user_following]

    # get blocks: users I blocked and users who blocked me
    blocked_by_me_qs = Block.objects.filter(blocker=me).values_list('blocked', flat=True)
    blocked_me_qs = Block.objects.filter(blocked=me).values_list('blocker', flat=True)
    blocked_by_me = set(blocked_by_me_qs)
    blocked_me = set(blocked_me_qs)

    # build feed: for each followed user, include their posts only if neither blocked relationship exists
    feed = []
    for username in following_usernames:
        if username in blocked_by_me or username in blocked_me:
            # skip posts from users who are blocked in either direction
            continue
        qs = Post.objects.filter(user=username)
        feed.append(qs)
    feed_list = list(chain(*feed))

    # USER SUGGESTIONS (exclude anyone blocked or who blocked me)
    all_users = User.objects.exclude(username__in=[me])  # exclude me
    # exclude users already followed, and any blocked or who blocked me
    followed_usernames_set = set(following_usernames)
    exclude_usernames = followed_usernames_set.union({me}).union(blocked_by_me).union(blocked_me)
    suggestions = [u for u in all_users if u.username not in exclude_usernames]
    random.shuffle(suggestions)

    # map to profiles
    username_profile_list = []
    for u in suggestions[:10]:
        plist = Profile.objects.filter(id_user=u.id)
        username_profile_list.extend(plist)
    suggestions_username_profile_list = username_profile_list

    # COMMENTS: load all comments (or optionally restrict to feed posts)
    comments = Comment.objects.filter(post__in=feed_list).order_by('timestamp')

    return render(request, 'index.html', {
        'user_profile': user_profile,
        'posts': feed_list,
        'comments': comments,
        'suggestions_username_profile_list': suggestions_username_profile_list[:4]
    })

@login_required(login_url='signin')
def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')
@login_required(login_url='signin')
def delete_post(request, post_id):
    """
    Deletes a Post and its image file.
    Only the post owner or a superuser (admin) may delete.
    Expects POST request (we'll use a POST form in template).
    """
    # require POST to avoid accidental deletes via GET
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    post = get_object_or_404(Post, id=post_id)

    # check authorization: owner or admin
    user_is_owner = (post.user == request.user.username)
    user_is_admin = request.user.is_superuser

    if not (user_is_owner or user_is_admin):
        messages.error(request, "You are not authorized to delete this post.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # delete image file from storage if present
    try:
        if post.image:
            post.image.delete(save=False)  # removes file but not model
    except Exception as e:
        # log to console for debugging; don't stop deletion of DB record
        print("Warning: failed to delete file for post", post.id, e)

    # delete DB record
    post.delete()

    messages.success(request, "Post deleted successfully.")
    # redirect back to referrer or to the owner's profile
    return redirect(request.META.get('HTTP_REFERER', f"/profile/{post.user}"))
@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter is None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()

        post.no_of_likes += 1
        post.save()

        # 🔔 Notification
        if post.user != username:
            create_notification(
                to_username=post.user,
                actor_username=username,
                verb="liked your post",
                notif_type="like",
                post_id=str(post.id),
                url=f"/profile/{post.user}"
            )

    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()

    # 🔙 Redirect to the same page
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)

    # If the current user is blocked by the profile owner, do not show posts
    me = request.user.username
    blocked_by_profile = Block.objects.filter(blocker=pk, blocked=me).exists()
    i_blocked_profile = Block.objects.filter(blocker=me, blocked=pk).exists()

    if blocked_by_profile:
        # optional: still allow viewing basic profile but hide posts & actions
        user_posts = Post.objects.none()
        user_post_length = 0
        blocked_message = "You are blocked by this user, their posts are not visible."
    else:
        # show posts only if viewer didn't block or wasn't blocked
        if i_blocked_profile:
            user_posts = Post.objects.none()
            user_post_length = 0
            blocked_message = "You have blocked this user; their posts are hidden."
        else:
            user_posts = Post.objects.filter(user=pk).order_by('-created_at')
            user_post_length = user_posts.count()
            blocked_message = None

    follower = me
    user = pk
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = FollowersCount.objects.filter(user=pk).count()
    user_following = FollowersCount.objects.filter(follower=pk).count()

    # comments for posts on this profile
    comments_qs = Comment.objects.filter(post__in=user_posts).order_by('timestamp')
    comments_by_post = {}
    for c in comments_qs:
        comments_by_post.setdefault(str(c.post.id), []).append(c)

    # can delete if owner or admin
    can_delete = request.user.is_authenticated and (request.user.username == pk or request.user.is_superuser)

    # check block status from me -> profile (for showing block/unblock button)
    is_blocking = Block.objects.filter(blocker=me, blocked=pk).exists()

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
        'comments_by_post': comments_by_post,
        'can_delete': can_delete,
        'blocked_message': blocked_message,
        'is_blocking': is_blocking,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            if follower != user:       # avoid self follow scenario
                create_notification(
                    to_username=user,
                    actor_username=follower,
                    verb="started following you",
                    notif_type="follow",
                    url=f"/profile/{follower}"
                )

            return redirect('/profile/'+user)
    else:
        return redirect('/')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        return redirect('settings')
    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
        
    else:
        return render(request, 'signup.html')

def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def notifications(request):
    """
    GET /notifications/  -> returns JSON list of notifications for logged-in user
    """
    qs = Notification.objects.filter(to_user=request.user.username).order_by('-timestamp')[:40]
    data = []
    for n in qs:
        data.append({
            "id": n.id,
            "actor": n.actor,
            "verb": n.verb,
            "notif_type": n.notif_type,
            "post_id": n.post_id,
            "url": n.url,
            "read": n.read,
            "timestamp": n.timestamp.strftime("%Y-%m-%d %H:%M"),
        })
    return JsonResponse({"notifications": data})


@require_POST
@login_required(login_url='signin')
def mark_notification_read(request, notif_id):
    notif = Notification.objects.get(id=notif_id, to_user=request.user.username)
    notif.read = True
    notif.save()
    return JsonResponse({"status": "ok", "id": notif.id})


@require_POST
@login_required(login_url='signin')
def mark_all_read(request):
    Notification.objects.filter(to_user=request.user.username, read=False).update(read=True)
    return JsonResponse({"status": "ok"})

# core/views.py (append)
from django.views.decorators.http import require_POST
from .models import Comment

@require_POST
@login_required(login_url='signin')
def add_comment(request):
    user = request.user.username
    post_id = request.POST.get('post_id')
    body = request.POST.get('body', '').strip()

    if not post_id or not body:
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # create comment
    comment = Comment.objects.create(post=post, user=user, body=body)

    # create notification for the post owner (avoid notifying yourself)
    try:
        post_owner = post.user
        if post_owner and post_owner != user:
            # use notif_type 'comment' (added to model)
            create_notification(
                to_username=post_owner,
                actor_username=user,
                verb="commented on your post",
                notif_type="comment",
                post_id=str(post.id),
                url=f"/profile/{post.user}"   # or a post detail URL if you have one
            )
    except Exception:
        # don't break flow if notification fails
        pass

    return redirect(request.META.get('HTTP_REFERER', '/'))

@require_POST
@login_required(login_url='signin')
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user == request.user.username:
        comment.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
@login_required(login_url='signin')
def block_user(request):
    blocker = request.user.username
    blocked = request.POST.get('blocked')
    if not blocked or blocked == blocker:
        messages.error(request, "Invalid block request.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    Block.objects.get_or_create(blocker=blocker, blocked=blocked)
    # optionally remove follow relationships
    FollowersCount.objects.filter(follower=blocker, user=blocked).delete()
    FollowersCount.objects.filter(follower=blocked, user=blocker).delete()
    messages.success(request, f"You blocked {blocked}.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
@login_required(login_url='signin')
def unblock_user(request):
    blocker = request.user.username
    blocked = request.POST.get('blocked')
    if not blocked:
        messages.error(request, "Invalid unblock request.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    Block.objects.filter(blocker=blocker, blocked=blocked).delete()
    messages.success(request, f"You unblocked {blocked}.")
    return redirect(request.META.get('HTTP_REFERER', '/'))



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    data = json.loads(request.body.decode('utf-8'))
    username = data.get("username")
    password = data.get("password")

    user = auth.authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    return JsonResponse({"message": "Login successful", "username": username})



