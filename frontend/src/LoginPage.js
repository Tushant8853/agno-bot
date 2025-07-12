import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import ApiService from './api';

function LoginPage({ setAuth }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const data = await ApiService.login(email, password);
      localStorage.setItem('access_token', data.tokens.access_token);
      localStorage.setItem('session_token', data.tokens.session_token || '');
      setAuth({ user: data.user, tokens: data.tokens });
      navigate('/');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="auth-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
      {error && <div className="error">{error}</div>}
      <p>Don't have an account? <Link to="/signup">Sign up</Link></p>
    </div>
  );
}

export default LoginPage; 