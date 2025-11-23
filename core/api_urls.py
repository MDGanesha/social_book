from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'profiles', api_views.ProfileViewSet, basename='profile')
router.register(r'posts', api_views.PostViewSet, basename='post')
router.register(r'comments', api_views.CommentViewSet, basename='comment')
router.register(r'followers', api_views.FollowersCountViewSet, basename='follower')
router.register(r'notifications', api_views.NotificationViewSet, basename='notification')
router.register(r'blocks', api_views.BlockViewSet, basename='block')

# API URL patterns
urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/signup/', api_views.api_signup, name='api-signup'),
    path('auth/login/', api_views.api_login, name='api-login'),
    path('auth/logout/', api_views.api_logout, name='api-logout'),
    path('auth/user/', api_views.api_user_info, name='api-user-info'),
]

