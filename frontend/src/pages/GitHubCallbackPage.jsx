// src/pages/GitHubCallbackPage.jsx
// Receives GitHub's redirect after "Sign in with GitHub": verifies the
// state token, exchanges the code for JWTs, then sends the user to the
// dashboard. Handles a denied/cancelled sign-in and missing codes.
import React, { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { finishGitHubLogin } from "../api/api";

export default function GitHubCallbackPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState("");

  useEffect(() => {
    const run = async () => {
      const errorParam = params.get("error");
      if (errorParam) {
        setError(
          errorParam === "access_denied"
            ? "GitHub sign-in was cancelled."
            : "GitHub sign-in failed."
        );
        return;
      }
      const code = params.get("code");
      const state = params.get("state");
      if (!code) {
        setError("GitHub did not return an authorization code.");
        return;
      }
      try {
        await finishGitHubLogin(code, state);
        navigate("/dashboard");
      } catch (err) {
        setError(
          err.response?.data?.detail ||
            "GitHub sign-in failed. Please try again."
        );
      }
    };
    run();
  }, []);

  if (error) {
    return (
      <div className="login-page">
        <h2>GitHub sign-in failed</h2>
        <p style={{ color: "red" }}>{error}</p>
        <Link to="/login">Back to login</Link>
      </div>
    );
  }

  return (
    <div className="login-page">
      <p>Signing you in with GitHub…</p>
    </div>
  );
}
