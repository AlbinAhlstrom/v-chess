import { useState, useEffect, useCallback } from 'react';
import { getMe } from '../api';

export function useUserSession() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(() => {
    getMe().then(data => {
      setUser(data.user || null);
      setLoading(false);
    }).catch(e => {
      console.error("Failed to fetch user:", e);
      setUser(null);
      setLoading(false);
    });
  }, []);

  const handleUsernameComplete = (newUsername) => {
    setUser(prev => ({ ...prev, username: newUsername }));
  };

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  useEffect(() => {
    window.addEventListener('focus', fetchUser);
    return () => window.removeEventListener('focus', fetchUser);
  }, [fetchUser]);

  return { user, loading, handleUsernameComplete };
}
