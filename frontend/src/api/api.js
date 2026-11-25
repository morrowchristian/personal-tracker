// src/api/api.js
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

let store = {
  access: null,
  refresh: null,
  onLogout: () => {},
};

export const setAuthTokens = (access, refresh) => {
  store.access = access;
  store.refresh = refresh;
};

export const setLogoutHandler = (logoutFn) => {
  store.onLogout = logoutFn;
};

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  if (store.access) config.headers.Authorization = `Bearer ${store.access}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    // if access expired, try refreshing
    if (error.response?.status === 401 && !original._retry && store.refresh) {
      original._retry = true;
      try {
        const res = await axios.post(`${API_BASE}/token/refresh/`, { refresh: store.refresh });
        store.access = res.data.access;
        localStorage.setItem("access", store.access);
        original.headers.Authorization = `Bearer ${store.access}`;
        return api(original);
      } catch (err) {
        console.warn("Token refresh failed, logging out");
        store.onLogout();
      }
    }
    return Promise.reject(error);
  }
);

export const login = async (username, password) => {
  const res = await api.post("/token/", { username, password });
  const { access, refresh } = res.data;
  setAuthTokens(access, refresh);
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
  return res.data;
};

export const logout = () => {
  store.access = null;
  store.refresh = null;
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  store.onLogout();
};

// --- Sign in with GitHub (OAuth 2.0) ---

const GITHUB_STATE_KEY = "github_oauth_state";

// Start the flow: fetch the GitHub authorize URL from the backend, save
// the state token, then send the browser to GitHub.
export const startGitHubLogin = async () => {
  const res = await api.get("/auth/github/");
  const { authorize_url, state } = res.data;
  sessionStorage.setItem(GITHUB_STATE_KEY, state);
  window.location.href = authorize_url;
};

// Finish the flow on the callback page: verify the state token, then
// exchange the code for JWTs and store them like a normal login.
export const finishGitHubLogin = async (code, state) => {
  const expected = sessionStorage.getItem(GITHUB_STATE_KEY);
  sessionStorage.removeItem(GITHUB_STATE_KEY);
  if (!expected || state !== expected) {
    throw new Error("GitHub sign-in state mismatch — please try again.");
  }
  const res = await api.post("/auth/github/callback/", { code });
  const { access, refresh } = res.data;
  setAuthTokens(access, refresh);
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
  return res.data;
};

export const ping = async () => {
  const res = await api.get("/ping/");
  return res.data;
};

export const getMe = async () => {
  try {
    const res = await api.get("/me/");
    return res.data; // { id, username, email }
  } catch (err) {
    console.warn("Failed to fetch user info");
    return null;
  }
};

// --- Tasks (JWT-protected, scoped to the logged-in user) ---

export const getTasks = async () => {
  const res = await api.get("/tasks/");
  return res.data;
};

export const createTask = async (task) => {
  const res = await api.post("/tasks/", task);
  return res.data;
};

export const updateTask = async (id, task) => {
  const res = await api.put(`/tasks/${id}/`, task);
  return res.data;
};

export const patchTask = async (id, task) => {
  const res = await api.patch(`/tasks/${id}/`, task);
  return res.data;
};

export const deleteTask = async (id) => {
  await api.delete(`/tasks/${id}/`);
};

export const toggleTask = async (id) => {
  const res = await api.post(`/tasks/${id}/toggle/`);
  return res.data;
};


export default api;