// src/pages/LoginPage.jsx
import React, { useState } from "react";
import { demoLogin, getMe, login, startGitHubLogin } from "../api/api";
import { useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [githubError, setGithubError] = useState("");
  const [demoError, setDemoError] = useState("");
  const [demoLoading, setDemoLoading] = useState(false);
  const navigate = useNavigate();
  const { setUser } = useAuth();

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

  const handleDemoLogin = async () => {
    setDemoError("");
    setDemoLoading(true);
    try {
      await demoLogin();
      const me = await getMe();
      if (me) setUser(me);
      navigate("/dashboard");
    } catch {
      setDemoError("Could not start the demo. Please try again.");
    } finally {
      setDemoLoading(false);
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
      <p>or</p>
      <button
        type="button"
        className="btn btn--primary"
        onClick={handleDemoLogin}
        disabled={demoLoading}
      >
        {demoLoading ? "Starting your demo…" : "Try the demo"}
      </button>
      <p>No account needed — explore the app with a few sample tasks.</p>
      {demoError && <p style={{ color: "red" }}>{demoError}</p>}
    </div>
  );
}
