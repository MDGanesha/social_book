# Social Book Frontend

React frontend application for the Social Book social media platform.

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

1. Make sure the Django backend is running on `http://localhost:8000`

2. Start the React development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## Features

- **Authentication**: Login and Signup
- **Feed**: View posts from users you follow
- **Posts**: Create, like, comment, and delete posts
- **Profiles**: View and edit user profiles
- **Follow/Unfollow**: Follow other users
- **Search**: Search for users
- **Notifications**: View and manage notifications
- **Block/Unblock**: Block unwanted users
- **User Suggestions**: Discover new users to follow

## Project Structure

```
src/
├── components/          # React components
│   ├── Auth/           # Login and Signup
│   ├── Feed/            # Feed and suggestions
│   ├── Post/            # Post components
│   ├── Profile/         # Profile view and settings
│   ├── Search/          # User search
│   ├── Notifications/   # Notifications
│   └── Navbar/          # Navigation bar
├── contexts/            # React contexts
│   └── AuthContext.js   # Authentication context
├── services/            # API services
│   └── api.js          # Axios API configuration
├── App.js              # Main app component
└── index.js            # Entry point
```

## API Integration

All API calls are made through the `services/api.js` file which uses Axios. The API base URL is configured to `http://localhost:8000/api`.

## Environment Variables

You can create a `.env` file to configure:

```
REACT_APP_API_URL=http://localhost:8000/api
```

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

