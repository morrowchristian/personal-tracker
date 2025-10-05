// src/context/AuthProvider.jsx
import React, { createContext, useState, useEffect } from "react";
import { setAuthTokens, setLogoutHandler, login as apiLogin, getMe } from "../api/api";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Logout function
  const logout = () => {
    setUser(null);
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    window.location.href = "/login";
  };

  // Load tokens from localStorage and set logout handler
  const loadTokens = () => {
    const access = localStorage.getItem("access");
    const refresh = localStorage.getItem("refresh");
    if (access && refresh) {
      setAuthTokens(access, refresh);
      return true;
    }
    return false;
  };

  // Fetch current user if tokens exist
  const fetchUser = async () => {
    if (!loadTokens()) {
      setLoading(false);
      return;
    }
    setLogoutHandler(logout);
    try {
      const me = await getMe();
      setUser(me);
    } catch (err) {
      console.warn("Failed to fetch user info:", err);
      logout();
    } finally {
      setLoading(false);
    }
  };

  // Login function
  const login = async (username, password) => {
    setLoading(true);
    try {
      await apiLogin(username, password);
      const me = await getMe();
      setUser(me);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const value = {
    user,
    loading,
    login,
    logout,
    setUser, // optional if you want to allow manual updates
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
