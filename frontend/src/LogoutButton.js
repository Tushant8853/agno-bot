import React from 'react';
import { useNavigate } from 'react-router-dom';
import ApiService from './api';

function LogoutButton({ setAuth }) {
  const navigate = useNavigate();

  const handleLogout = async () => {
    const sessionToken = localStorage.getItem('session_token');
    try {
      if (sessionToken) {
        await ApiService.logout(sessionToken);
      }
    } catch (err) {
      // Ignore errors on logout
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('session_token');
    setAuth(null);
    navigate('/login');
  };

  return (
    <button className="logout-btn" onClick={handleLogout}>
      Logout
    </button>
  );
}

export default LogoutButton; 