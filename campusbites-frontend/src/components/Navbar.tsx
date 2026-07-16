import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Navbar() {
  const { isAuthenticated, role, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  const canManageMenu = isAuthenticated && (role === "staff" || role === "admin");

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        CampusBites
      </Link>
      <div className="navbar-links">
        <Link to="/">Menu</Link>
        {canManageMenu && <Link to="/staff/menu">Manage Menu</Link>}
        {isAuthenticated ? (
          <button className="navbar-logout" onClick={handleLogout}>
            Log out
          </button>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}