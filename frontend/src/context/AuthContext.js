
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    const token = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('user_data');
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    // Simulate API call
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email && password) {
          const userData = {
            id: Date.now(),
            email,
            name: email.split('@')[0],
            avatar: null,
            preferences: {
              theme: 'dark',
              notifications: true,
            }
          };
          const token = `jwt_token_${Date.now()}`;

          localStorage.setItem('auth_token', token);
          localStorage.setItem('user_data', JSON.stringify(userData));

          setUser(userData);
          setIsAuthenticated(true);
          resolve({ success: true, user: userData, token });
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 500);
    });
  };

  const register = async (name, email, password) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (name && email && password) {
          const userData = {
            id: Date.now(),
            email,
            name,
            avatar: null,
            preferences: {
              theme: 'dark',
              notifications: true,
            }
          };
          const token = `jwt_token_${Date.now()}`;

          localStorage.setItem('auth_token', token);
          localStorage.setItem('user_data', JSON.stringify(userData));

          setUser(userData);
          setIsAuthenticated(true);
          resolve({ success: true, user: userData, token });
        } else {
          reject(new Error('Invalid registration data'));
        }
      }, 500);
    });
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    setUser(null);
    setIsAuthenticated(false);
  };

  const updatePreferences = (prefs) => {
    if (user) {
      const updatedUser = {
        ...user,
        preferences: { ...user.preferences, ...prefs }
      };
      setUser(updatedUser);
      localStorage.setItem('user_data', JSON.stringify(updatedUser));
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      loading,
      login,
      register,
      logout,
      updatePreferences
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;

