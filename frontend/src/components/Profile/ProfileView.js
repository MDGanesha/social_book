import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { profileAPI, postAPI, followerAPI, blockAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import PostCard from '../Post/PostCard';
import './Profile.css';

const ProfileView = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [posts, setPosts] = useState([]);
  const [followers, setFollowers] = useState(0);
  const [following, setFollowing] = useState(0);
  const [isFollowing, setIsFollowing] = useState(false);
  const [isBlocking, setIsBlocking] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProfile();
  }, [username]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      // Get profile by username
      const profilesResponse = await profileAPI.list({ username });
      if (profilesResponse.data.length > 0) {
        const profileData = profilesResponse.data[0];
        setProfile(profileData);

        // Load posts
        const postsResponse = await postAPI.list({ user: username });
        setPosts(postsResponse.data);

        // Load followers/following counts
        const followersResponse = await followerAPI.getFollowers({ user: username });
        const followingResponse = await followerAPI.getFollowing({ user: username });
        setFollowers(followersResponse.data.length);
        setFollowing(followingResponse.data.length);

        // Check if following
        if (currentUser) {
          const followCheck = await followerAPI.list({ user: username, follower: currentUser.username });
          setIsFollowing(followCheck.data.length > 0);

          // Check if blocking
          const blocksResponse = await blockAPI.list();
          const isBlocked = blocksResponse.data.some(b => b.blocked === username);
          setIsBlocking(isBlocked);
        }
      } else {
        setError('Profile not found');
      }
    } catch (error) {
      setError('Failed to load profile');
      console.error('Profile error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async () => {
    try {
      await followerAPI.toggle({ user: username });
      setIsFollowing(!isFollowing);
      loadProfile();
    } catch (error) {
      console.error('Follow error:', error);
    }
  };

  const handleBlock = async () => {
    try {
      await blockAPI.toggle({ blocked: username });
      setIsBlocking(!isBlocking);
      if (!isBlocking) {
        navigate('/');
      }
    } catch (error) {
      console.error('Block error:', error);
    }
  };

  const handlePostDelete = (postId) => {
    setPosts(posts.filter((p) => p.id !== postId));
  };

  if (loading) {
    return <div className="loading">Loading profile...</div>;
  }

  if (error || !profile) {
    return <div className="error-message">{error || 'Profile not found'}</div>;
  }

  const isOwnProfile = currentUser?.username === username;

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-avatar-section">
          {profile.profileimg_url && (
            <img
              src={profile.profileimg_url}
              alt={profile.username}
              className="profile-avatar-large"
            />
          )}
        </div>
        <div className="profile-info">
          <div className="profile-username-section">
            <h2>{profile.username}</h2>
            {!isOwnProfile && (
              <div className="profile-actions">
                <button
                  onClick={handleFollow}
                  className={`follow-btn ${isFollowing ? 'following' : ''}`}
                >
                  {isFollowing ? 'Unfollow' : 'Follow'}
                </button>
                <button
                  onClick={handleBlock}
                  className={`block-btn ${isBlocking ? 'blocked' : ''}`}
                >
                  {isBlocking ? 'Unblock' : 'Block'}
                </button>
              </div>
            )}
            {isOwnProfile && (
              <button
                onClick={() => navigate('/settings')}
                className="settings-btn"
              >
                Edit Profile
              </button>
            )}
          </div>
          <div className="profile-stats">
            <div className="stat">
              <strong>{posts.length}</strong> posts
            </div>
            <div className="stat">
              <strong>{followers}</strong> followers
            </div>
            <div className="stat">
              <strong>{following}</strong> following
            </div>
          </div>
          {profile.bio && (
            <div className="profile-bio">
              <strong>{profile.username}</strong>
              <p>{profile.bio}</p>
              {profile.location && <p className="location">📍 {profile.location}</p>}
            </div>
          )}
        </div>
      </div>

      <div className="profile-posts">
        <h3>Posts</h3>
        {posts.length === 0 ? (
          <div className="empty-posts">No posts yet</div>
        ) : (
          <div className="posts-grid">
            {posts.map((post) => (
              <PostCard
                key={post.id}
                post={post}
                onDelete={handlePostDelete}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfileView;

