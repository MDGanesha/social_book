import React, { useState } from 'react';
import { profileAPI } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import './Search.css';

const Search = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const response = await profileAPI.list({ username: query });
      setResults(response.data);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-container">
      <div className="search-card">
        <h2>Search Users</h2>
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by username..."
            className="search-input"
          />
          <button type="submit" className="search-btn" disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {results.length > 0 && (
          <div className="search-results">
            <h3>Results</h3>
            {results.map((profile) => (
              <div
                key={profile.id}
                className="search-result-item"
                onClick={() => navigate(`/profile/${profile.username}`)}
              >
                {profile.profileimg_url && (
                  <img
                    src={profile.profileimg_url}
                    alt={profile.username}
                    className="result-avatar"
                  />
                )}
                <div className="result-info">
                  <strong>{profile.username}</strong>
                  {profile.bio && <p>{profile.bio}</p>}
                </div>
              </div>
            ))}
          </div>
        )}

        {query && results.length === 0 && !loading && (
          <div className="no-results">No users found</div>
        )}
      </div>
    </div>
  );
};

export default Search;

