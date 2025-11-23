from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('upload', views.upload, name='upload'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post', views.like_post, name='like-post'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('add-comment/', views.add_comment, name='add_comment'),
    path('delete-post/<uuid:post_id>/', views.delete_post, name='delete-post'),
    path('block/', views.block_user, name='block-user'),
    path('unblock/', views.unblock_user, name='unblock-user'),
    path("api/login/", views.api_login, name="api-login"),
     path('api/login/', views.api_login, name='api_login'),
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/logout/', views.api_logout, name='api_logout'),

    path('api/posts/', views.api_posts_list_create, name='api_posts'),
    path('api/posts/<uuid:post_id>/', views.api_post_detail, name='api_post_detail'),
    path('api/posts/<uuid:post_id>/like/', views.api_like_toggle, name='api_post_like'),
    path('api/posts/<uuid:post_id>/comments/', views.api_comments_list_create, name='api_post_comments'),
    path('api/comments/<int:comment_id>/', views.api_comment_delete, name='api_comment_delete'),

    path('api/follow/', views.api_follow_toggle, name='api_follow_toggle'),
    path('api/block/', views.api_block, name='api_block'),
    path('api/unblock/', views.api_unblock, name='api_unblock'),

    path('api/notifications/', views.api_notifications_list, name='api_notifications'),
    path('api/notifications/mark-read/<int:notif_id>/', views.api_notification_mark_read, name='api_notification_mark_read'),

]