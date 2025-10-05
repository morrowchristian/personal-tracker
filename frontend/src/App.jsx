// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthProvider";
import LoginPage from "./pages/LoginPage";
import Dashboard from "./pages/Dashboard";

function PrivateRoute({ children }) {
  const access = localStorage.getItem("access");
  return access ? children : <Navigate to="/login" />;
}

function RootRedirect() {
  const access = localStorage.getItem("access");
  // If authenticated, go to dashboard, otherwise go to login
  return <Navigate to={access ? "/dashboard" : "/login"} />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<p>404: Page Not Found</p>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
