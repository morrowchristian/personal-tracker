// src/pages/LoginPage.jsx
import React, { useState } from "react";
import { login, startGitHubLogin } from "../api/api";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [githubError, setGithubError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(username, password);
      navigate("/dashboard");
    } catch {
      setError("Invalid credentials");
    }
  };

  const handleGitHubLogin = async () => {
    setGithubError("");
    try {
      await startGitHubLogin();
    } catch {
      setGithubError("GitHub sign-in is not available right now.");
    }
  };

  return (
    <div className="login-page">
      <form onSubmit={handleSubmit}>
        <h2>Login</h2>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Login</button>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </form>
      <p>or</p>
      <button type="button" className="btn" onClick={handleGitHubLogin}>
        Sign in with GitHub
      </button>
      {githubError && <p style={{ color: "red" }}>{githubError}</p>}
    </div>
  );
}
