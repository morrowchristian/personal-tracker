// src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import api, { ping } from "../api/api";
import useAuth from "../hooks/useAuth";

export default function Dashboard() {
  const { logout } = useAuth();
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchPing = async () => {
      try {
        const res = await ping();
        setData(res);
      } catch (err) {
        console.error("Ping failed:", err);
      }
    };
    fetchPing();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <button onClick={logout}>Logout</button>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
