import React, { useState, useEffect } from 'react';
import { postAPI } from '../../services/api';
import PostCard from '../Post/PostCard';
import CreatePost from '../Post/CreatePost';
import UserSuggestions from './UserSuggestions';
import './Feed.css';

const Feed = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadFeed();
  }, []);

  const loadFeed = async () => {
    try {
      setLoading(true);
      const response = await postAPI.getFeed();
      setPosts(response.data);
      setError('');
    } catch (error) {
      setError('Failed to load feed');
      console.error('Feed error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePostCreated = () => {
    loadFeed();
  };

  const handlePostDelete = (postId) => {
    setPosts(posts.filter((p) => p.id !== postId));
  };

  const handlePostUpdate = () => {
    loadFeed();
  };

  if (loading) {
    return <div className="loading">Loading feed...</div>;
  }

  return (
    <div className="feed-container">
      <div className="feed-main">
        <CreatePost onPostCreated={handlePostCreated} />
        {error && <div className="error-message">{error}</div>}
        {posts.length === 0 ? (
          <div className="empty-feed">
            <p>Your feed is empty. Follow some users to see their posts!</p>
          </div>
        ) : (
          posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onDelete={handlePostDelete}
              onUpdate={handlePostUpdate}
            />
          ))
        )}
      </div>
      <div className="feed-sidebar">
        <UserSuggestions />
      </div>
    </div>
  );
};

export default Feed;

