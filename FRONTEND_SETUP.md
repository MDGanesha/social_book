# Social Book - React Frontend Setup Guide

## Overview

This is a complete React frontend application that integrates with the Django REST API backend. All API endpoints have been implemented.

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Django backend running on `http://localhost:8000`

## Installation Steps

### 1. Install Dependencies

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

### 2. Start the Development Server

```bash
npm start
```

The app will open at `http://localhost:3000`

## Features Implemented

### ✅ Authentication
- User signup with validation
- User login
- User logout
- Protected routes
- Session management

### ✅ Posts
- Create new posts with images
- View feed (posts from followed users)
- Like/unlike posts
- Delete own posts
- View post details

### ✅ Comments
- Add comments to posts
- View comments
- Delete own comments
- Real-time comment count

### ✅ Profiles
- View user profiles
- Edit own profile (bio, location, profile image)
- View user's posts
- Profile statistics (posts, followers, following)

### ✅ Follow/Unfollow
- Follow users
- Unfollow users
- View followers list
- View following list

### ✅ Search
- Search users by username
- View search results
- Navigate to user profiles

### ✅ Notifications
- View all notifications
- Mark notifications as read
- Mark all as read
- Unread notification count
- Real-time updates

### ✅ User Suggestions
- Discover new users
- Follow from suggestions
- Filtered suggestions (excludes blocked users)

### ✅ Block/Unblock
- Block users
- Unblock users
- Hide blocked users' content

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── Login.js
│   │   │   ├── Signup.js
│   │   │   └── Auth.css
│   │   ├── Feed/
│   │   │   ├── Feed.js
│   │   │   ├── UserSuggestions.js
│   │   │   └── *.css
│   │   ├── Post/
│   │   │   ├── PostCard.js
│   │   │   ├── CreatePost.js
│   │   │   └── *.css
│   │   ├── Profile/
│   │   │   ├── ProfileView.js
│   │   │   ├── ProfileSettings.js
│   │   │   └── Profile.css
│   │   ├── Search/
│   │   │   ├── Search.js
│   │   │   └── Search.css
│   │   ├── Notifications/
│   │   │   ├── Notifications.js
│   │   │   └── Notifications.css
│   │   ├── Navbar/
│   │   │   ├── Navbar.js
│   │   │   └── Navbar.css
│   │   └── ProtectedRoute.js
│   ├── contexts/
│   │   └── AuthContext.js
│   ├── services/
│   │   └── api.js
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

## API Integration

All API endpoints are integrated through `src/services/api.js`:

- **Authentication**: `/api/auth/*`
- **Profiles**: `/api/profiles/*`
- **Posts**: `/api/posts/*`
- **Comments**: `/api/comments/*`
- **Followers**: `/api/followers/*`
- **Notifications**: `/api/notifications/*`
- **Blocks**: `/api/blocks/*`

## Configuration

### API Base URL

The API base URL is configured in `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

To change it, modify this constant or use environment variables.

### CORS Configuration

Make sure the Django backend has CORS configured to allow requests from `http://localhost:3000`.

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Troubleshooting

### CORS Errors

If you encounter CORS errors, make sure:
1. Django CORS settings allow `http://localhost:3000`
2. Backend is running on `http://localhost:8000`
3. `withCredentials: true` is set in axios config (already configured)

### Authentication Issues

- Clear browser cookies if login fails
- Check browser console for errors
- Verify backend is running and accessible

### Image Upload Issues

- Check file size limits
- Verify backend media settings
- Check browser console for errors

## Production Build

To create a production build:

```bash
npm run build
```

The build folder will contain optimized production files. You can serve these files with any static file server or integrate with Django's static files.

## Next Steps

- Add token authentication for mobile apps
- Implement real-time updates with WebSockets
- Add image optimization
- Implement infinite scroll for feed
- Add error boundaries
- Add loading skeletons
- Implement offline support

