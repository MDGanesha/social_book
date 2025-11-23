import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI, profileAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await authAPI.getUserInfo();
      setUser(response.data.user);
      setProfile(response.data.profile);
    } catch (error) {
      setUser(null);
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await authAPI.login({ username, password });
      setUser(response.data.user);
      setProfile(response.data.profile);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed',
      };
    }
  };

  const signup = async (username, email, password, password2) => {
    try {
      const response = await authAPI.signup({
        username,
        email,
        password,
        password2,
      });
      setUser(response.data.user);
      setProfile(response.data.profile);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Signup failed',
      };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setProfile(null);
    }
  };

  const updateProfile = async (data) => {
    try {
      // If data is FormData, use it directly, otherwise convert to FormData
      let formData = data;
      if (!(data instanceof FormData)) {
        formData = new FormData();
        if (data.bio !== undefined) formData.append('bio', data.bio);
        if (data.location !== undefined) formData.append('location', data.location);
        if (data.profileimg) formData.append('profileimg', data.profileimg);
      }
      
      const response = await profileAPI.partialUpdateMe(formData);
      setProfile(response.data);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || 'Update failed',
      };
    }
  };

  const value = {
    user,
    profile,
    loading,
    login,
    signup,
    logout,
    updateProfile,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

