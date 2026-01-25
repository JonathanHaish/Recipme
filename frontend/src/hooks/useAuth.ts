"use client";

import { useState, useEffect } from 'react';
import { authAPI } from '@/lib/auth';
import type { User } from '@/types/auth';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const userData = await authAPI.getMe();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      // Silently handle authentication errors (user is just not logged in)
      setUser(null);
      setIsAuthenticated(false);
      // Don't log errors on auth pages - it's expected behavior
      if (typeof window !== 'undefined') {
        const currentPath = window.location.pathname;
        const isAuthPage = currentPath.startsWith('/login') ||
                          currentPath.startsWith('/register') ||
                          currentPath.startsWith('/forgot-password') ||
                          currentPath.startsWith('/reset-password');
        if (!isAuthPage) {
          console.error('Authentication check failed:', error);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
      // Even if logout fails, clear local state
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  return {
    user,
    loading,
    isAuthenticated,
    logout,
    refreshAuth: checkAuth,
  };
}

