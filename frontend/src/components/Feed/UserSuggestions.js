import React, { useState, useEffect } from 'react';
import { postAPI, followerAPI } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import './UserSuggestions.css';

const UserSuggestions = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadSuggestions();
  }, []);

  const loadSuggestions = async () => {
    try {
      const response = await postAPI.getSuggestions();
      setSuggestions(response.data);
    } catch (error) {
      console.error('Suggestions error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async (username) => {
    try {
      await followerAPI.toggle({ user: username });
      loadSuggestions();
    } catch (error) {
      console.error('Follow error:', error);
    }
  };

  if (loading || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="suggestions-card">
      <h3>Suggestions for you</h3>
      <div className="suggestions-list">
        {suggestions.map((profile) => (
          <div key={profile.id} className="suggestion-item">
            <div
              className="suggestion-user"
              onClick={() => navigate(`/profile/${profile.username}`)}
            >
              {profile.profileimg_url && (
                <img
                  src={profile.profileimg_url}
                  alt={profile.username}
                  className="suggestion-avatar"
                />
              )}
              <span className="suggestion-username">{profile.username}</span>
            </div>
            <button
              onClick={() => handleFollow(profile.username)}
              className="follow-btn"
            >
              Follow
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UserSuggestions;

