import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";

// Placeholder home — real menu page lands Week 3, Day 4. This just proves
// the auth flow works end to end: unauthenticated visitors bounce to /login.
function HomePlaceholder() {
  const { isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="auth-page">
      <div className="auth-form">
        <h1>CampusBites</h1>
        <p>You're logged in. Menu page lands Week 3.</p>
        <button onClick={() => logout()}>Log out</button>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/" element={<HomePlaceholder />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}