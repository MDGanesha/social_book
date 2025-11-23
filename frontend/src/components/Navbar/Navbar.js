import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { notificationAPI } from '../../services/api';
import { FaHome, FaSearch, FaBell, FaUser, FaSignOutAlt } from 'react-icons/fa';
import './Navbar.css';

const Navbar = () => {
  const { user, profile, logout } = useAuth();
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (user) {
      loadUnreadCount();
      const interval = setInterval(loadUnreadCount, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const loadUnreadCount = async () => {
    try {
      const response = await notificationAPI.list();
      const unread = response.data.filter(n => !n.read).length;
      setUnreadCount(unread);
    } catch (error) {
      console.error('Load notifications error:', error);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (!user) {
    return null;
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          Social Book
        </Link>
        <div className="navbar-links">
          <Link to="/" className="nav-link">
            <FaHome /> Home
          </Link>
          <Link to="/search" className="nav-link">
            <FaSearch /> Search
          </Link>
          <Link to="/notifications" className="nav-link">
            <FaBell />
            Notifications
            {unreadCount > 0 && <span className="badge">{unreadCount}</span>}
          </Link>
          <Link to={`/profile/${user.username}`} className="nav-link">
            {profile?.profileimg_url ? (
              <img
                src={profile.profileimg_url}
                alt={user.username}
                className="nav-avatar"
              />
            ) : (
              <FaUser />
            )}
            {user.username}
          </Link>
          <button onClick={handleLogout} className="nav-link logout-btn">
            <FaSignOutAlt /> Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

