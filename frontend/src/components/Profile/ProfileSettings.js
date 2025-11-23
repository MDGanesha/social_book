import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Profile.css';

const ProfileSettings = () => {
  const { profile, updateProfile } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    bio: '',
    location: '',
    image: null,
  });
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (profile) {
      setFormData({
        bio: profile.bio || '',
        location: profile.location || '',
        image: null,
      });
      setPreview(profile.profileimg_url);
    }
  }, [profile]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData({ ...formData, image: file });
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    const data = new FormData();
    if (formData.bio !== (profile.bio || '')) {
      data.append('bio', formData.bio);
    }
    if (formData.location !== (profile.location || '')) {
      data.append('location', formData.location);
    }
    if (formData.image) {
      data.append('profileimg', formData.image);
    }

    const result = await updateProfile(data);
    setLoading(false);

    if (result.success) {
      setSuccess('Profile updated successfully!');
      setTimeout(() => {
        navigate(`/profile/${profile.username}`);
      }, 1500);
    } else {
      setError(result.error?.error || result.error || 'Failed to update profile');
    }
  };

  if (!profile) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="settings-container">
      <div className="settings-card">
        <h2>Edit Profile</h2>
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Profile Image</label>
            {preview && (
              <img src={preview} alt="Preview" className="image-preview" />
            )}
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
            />
          </div>
          <div className="form-group">
            <label>Bio</label>
            <textarea
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              placeholder="Tell us about yourself"
              rows="4"
            />
          </div>
          <div className="form-group">
            <label>Location</label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="Your location"
            />
          </div>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ProfileSettings;

