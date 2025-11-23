import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication APIs
export const authAPI = {
  signup: (data) => api.post('/auth/signup/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: () => api.post('/auth/logout/'),
  getUserInfo: () => api.get('/auth/user/'),
};

// Profile APIs
export const profileAPI = {
  list: (params) => api.get('/profiles/', { params }),
  get: (id) => api.get(`/profiles/${id}/`),
  update: (id, data) => api.put(`/profiles/${id}/`, data),
  partialUpdate: (id, data) => api.patch(`/profiles/${id}/`, data),
  getMe: () => api.get('/profiles/me/'),
  updateMe: (data) => {
    if (data instanceof FormData) {
      return api.put('/profiles/update_me/', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    }
    return api.put('/profiles/update_me/', data);
  },
  partialUpdateMe: (data) => {
    if (data instanceof FormData) {
      return api.patch('/profiles/update_me/', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    }
    return api.patch('/profiles/update_me/', data);
  },
};

// Post APIs
export const postAPI = {
  list: (params) => api.get('/posts/', { params }),
  get: (id) => api.get(`/posts/${id}/`),
  create: (data) => {
    const formData = new FormData();
    formData.append('image', data.image);
    formData.append('caption', data.caption);
    return api.post('/posts/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  update: (id, data) => api.put(`/posts/${id}/`, data),
  partialUpdate: (id, data) => api.patch(`/posts/${id}/`, data),
  delete: (id) => api.delete(`/posts/${id}/`),
  like: (id) => api.post(`/posts/${id}/like/`),
  unlike: (id) => api.delete(`/posts/${id}/like/`),
  getFeed: () => api.get('/posts/feed/'),
  getSuggestions: () => api.get('/posts/suggestions/'),
};

// Comment APIs
export const commentAPI = {
  list: (params) => api.get('/comments/', { params }),
  get: (id) => api.get(`/comments/${id}/`),
  create: (data) => api.post('/comments/', data),
  delete: (id) => api.delete(`/comments/${id}/`),
};

// Follower APIs
export const followerAPI = {
  list: (params) => api.get('/followers/', { params }),
  toggle: (data) => api.post('/followers/toggle/', data),
  getFollowers: (params) => api.get('/followers/followers/', { params }),
  getFollowing: (params) => api.get('/followers/following/', { params }),
};

// Notification APIs
export const notificationAPI = {
  list: () => api.get('/notifications/'),
  get: (id) => api.get(`/notifications/${id}/`),
  markRead: (id) => api.post(`/notifications/${id}/mark_read/`),
  markAllRead: () => api.post('/notifications/mark_all_read/'),
};

// Block APIs
export const blockAPI = {
  list: () => api.get('/blocks/'),
  toggle: (data) => api.post('/blocks/toggle/', data),
  delete: (id) => api.delete(`/blocks/${id}/`),
};

export default api;

