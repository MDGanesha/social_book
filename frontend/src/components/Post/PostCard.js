import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { postAPI, commentAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { FaHeart, FaRegHeart, FaComment, FaTrash } from 'react-icons/fa';
import './Post.css';

const PostCard = ({ post, onDelete, onUpdate }) => {
  const [isLiked, setIsLiked] = useState(post.is_liked);
  const [likes, setLikes] = useState(post.no_of_likes);
  const [comments, setComments] = useState([]);
  const [showComments, setShowComments] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [loading, setLoading] = useState(false);
  const { user, profile } = useAuth();
  const navigate = useNavigate();

  const handleLike = async () => {
    try {
      if (isLiked) {
        await postAPI.unlike(post.id);
        setIsLiked(false);
        setLikes(likes - 1);
      } else {
        await postAPI.like(post.id);
        setIsLiked(true);
        setLikes(likes + 1);
      }
    } catch (error) {
      console.error('Like error:', error);
    }
  };

  const loadComments = async () => {
    try {
      const response = await commentAPI.list({ post: post.id });
      setComments(response.data);
    } catch (error) {
      console.error('Load comments error:', error);
    }
  };

  const toggleComments = () => {
    if (!showComments) {
      loadComments();
    }
    setShowComments(!showComments);
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;

    setLoading(true);
    try {
      const response = await commentAPI.create({
        post: post.id,
        body: commentText,
      });
      setComments([...comments, response.data]);
      setCommentText('');
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Add comment error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteComment = async (commentId) => {
    try {
      await commentAPI.delete(commentId);
      setComments(comments.filter((c) => c.id !== commentId));
    } catch (error) {
      console.error('Delete comment error:', error);
    }
  };

  const handleDeletePost = async () => {
    if (window.confirm('Are you sure you want to delete this post?')) {
      try {
        await postAPI.delete(post.id);
        if (onDelete) onDelete(post.id);
      } catch (error) {
        console.error('Delete post error:', error);
        alert('Failed to delete post');
      }
    }
  };

  const canDelete = user?.username === post.user || user?.is_superuser;

  return (
    <div className="post-card">
      <div className="post-header">
        <div
          className="post-user-info"
          onClick={() => navigate(`/profile/${post.user}`)}
          style={{ cursor: 'pointer' }}
        >
          {post.user_profile?.profileimg_url && (
            <img
              src={post.user_profile.profileimg_url}
              alt={post.user}
              className="post-avatar"
            />
          )}
          <span className="post-username">{post.user}</span>
        </div>
        {canDelete && (
          <button
            onClick={handleDeletePost}
            className="delete-btn"
            title="Delete post"
          >
            <FaTrash />
          </button>
        )}
      </div>

      {post.image_url && (
        <img src={post.image_url} alt="Post" className="post-image" />
      )}

      <div className="post-content">
        <div className="post-actions">
          <button
            onClick={handleLike}
            className={`like-btn ${isLiked ? 'liked' : ''}`}
          >
            {isLiked ? <FaHeart /> : <FaRegHeart />}
            <span>{likes}</span>
          </button>
          <button onClick={toggleComments} className="comment-btn">
            <FaComment />
            <span>{post.comments_count || 0}</span>
          </button>
        </div>

        <div className="post-caption">
          <strong>{post.user}</strong> {post.caption}
        </div>

        {showComments && (
          <div className="comments-section">
            <div className="comments-list">
              {comments.map((comment) => (
                <div key={comment.id} className="comment-item">
                  <strong>{comment.user}</strong>
                  <span>{comment.body}</span>
                  {comment.user === user?.username && (
                    <button
                      onClick={() => handleDeleteComment(comment.id)}
                      className="delete-comment-btn"
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
            </div>
            <form onSubmit={handleAddComment} className="comment-form">
              <input
                type="text"
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder="Add a comment..."
                className="comment-input"
              />
              <button type="submit" disabled={loading} className="comment-submit">
                Post
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default PostCard;

