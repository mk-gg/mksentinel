import { useState, useEffect, useCallback } from 'react';
import { AuthRepository, User } from '@/repositories/authRepository';

export function useAuthRepository() {
  const repository = AuthRepository.getInstance();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCurrentUser = useCallback(async (forceRefresh = false) => {
    setLoading(true);
    try {
      const result = await repository.getCurrentUser(forceRefresh);
      setUser(result.user);
      if (result.error) {
        setError(result.error);
      } else {
        setError(null);
      }
    } catch (err) {
      setError('Failed to fetch current user');
      console.error('Error in useAuthRepository.fetchCurrentUser:', err);
    } finally {
      setLoading(false);
    }
  }, [repository]);

  const login = useCallback(() => {
    repository.redirectToGoogleAuth();
  }, [repository]);

  const loginWithGithub = useCallback(() => {
    repository.redirectToGithubAuth();
  }, [repository]);

  const logout = useCallback(async () => {
    try {
      const result = await repository.logout();
      if (result.success) {
        setUser(null);
      } else if (result.error) {
        setError(result.error);
      }
      return result;
    } catch (err) {
      setError('Failed to logout');
      console.error('Error in useAuthRepository.logout:', err);
      return { success: false, error: 'Failed to logout' };
    }
  }, [repository]);

  // Initial user loading effect
  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  return {
    user,
    loading,
    error,
    login,
    loginWithGithub,
    logout,
    fetchCurrentUser
  };
} 