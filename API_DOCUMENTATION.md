 Social Book REST API Documentation

This Django project has been converted to a REST API using Django REST Framework.

 Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Run the server:
```bash
python manage.py runserver
```

 API Base URL

All API endpoints are prefixed with `/api/`

 Authentication

Most endpoints require authentication. Use session authentication or basic authentication.

 Endpoints

 Authentication

- `POST /api/auth/signup/` - Register a new user
  - Body: `{ "username": "string", "email": "string", "password": "string", "password2": "string" }`
  
- `POST /api/auth/login/` - Login user
  - Body: `{ "username": "string", "password": "string" }`
  
- `POST /api/auth/logout/` - Logout user
  
- `GET /api/auth/user/` - Get current user information

 Profiles

- `GET /api/profiles/` - List all profiles
  - Query params: `?username=string` - Filter by username
  
- `GET /api/profiles/{id}/` - Get specific profile
  
- `PUT /api/profiles/{id}/` - Update profile (owner only)
  
- `PATCH /api/profiles/{id}/` - Partially update profile (owner only)
  
- `GET /api/profiles/me/` - Get current user's profile
  
- `PUT /api/profiles/update_me/` - Update current user's profile
- `PATCH /api/profiles/update_me/` - Partially update current user's profile

 Posts

- `GET /api/posts/` - List all posts
  - Query params: `?user=string` - Filter by username
  
- `GET /api/posts/{id}/` - Get specific post
  
- `POST /api/posts/` - Create a new post
  - Body: `{ "image": file, "caption": "string" }`
  
- `PUT /api/posts/{id}/` - Update post (owner only)
  
- `PATCH /api/posts/{id}/` - Partially update post (owner only)
  
- `DELETE /api/posts/{id}/` - Delete post (owner only)
  
- `POST /api/posts/{id}/like/` - Like a post
- `DELETE /api/posts/{id}/like/` - Unlike a post
  
- `GET /api/posts/feed/` - Get feed (posts from users you follow)
  
- `GET /api/posts/suggestions/` - Get user suggestions

 Comments

- `GET /api/comments/` - List all comments
  - Query params: `?post=uuid` - Filter by post ID
  
- `GET /api/comments/{id}/` - Get specific comment
  
- `POST /api/comments/` - Create a new comment
  - Body: `{ "post": "uuid", "body": "string" }`
  
- `DELETE /api/comments/{id}/` - Delete comment (owner only)

 Followers

- `GET /api/followers/` - List followers/following
  - Query params: `?user=string` - Get followers of user
  - Query params: `?follower=string` - Get users followed by user
  
- `POST /api/followers/toggle/` - Follow/unfollow a user
  - Body: `{ "user": "string" }`
  
- `GET /api/followers/followers/` - Get followers
  - Query params: `?user=string` - Defaults to current user
  
- `GET /api/followers/following/` - Get following
  - Query params: `?user=string` - Defaults to current user

 Notifications

- `GET /api/notifications/` - List all notifications for current user
  
- `GET /api/notifications/{id}/` - Get specific notification
  
- `POST /api/notifications/{id}/mark_read/` - Mark notification as read
  
- `POST /api/notifications/mark_all_read/` - Mark all notifications as read

 Blocks

- `GET /api/blocks/` - List blocked users (current user)
  
- `POST /api/blocks/toggle/` - Block/unblock a user
  - Body: `{ "blocked": "string" }`
  
- `DELETE /api/blocks/{id}/` - Unblock a user

 Response Format

All responses are in JSON format. Successful responses typically return status code 200 or 201.

Error responses include:
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (permission denied)
- `404` - Not Found
- `500` - Server Error

 Example Usage

 Create a Post:
```bash
POST /api/posts/
Content-Type: multipart/form-data

{
  "image": <file>,
  "caption": "My first post!"
}
```

 Like a Post:
```bash
POST /api/posts/{post_id}/like/
```

 Follow a User:
```bash
POST /api/followers/toggle/
Content-Type: application/json

{
  "user": "username"
}
```

 Get Feed:
```bash
GET /api/posts/feed/
```

 Pagination

List endpoints support pagination. Use query parameters:
- `?page=1` - Page number
- Default page size: 20 items per page

