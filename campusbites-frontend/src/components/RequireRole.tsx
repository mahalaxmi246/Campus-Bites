import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

interface RequireRoleProps {
  roles: Array<"student" | "staff" | "admin">;
  children: ReactNode;
}

/**
 * Client-side route gate — purely for UX (don't show a staff page to a
 * student who has no business seeing it). This is NOT the real security
 * boundary; the backend's require_role on every actual endpoint is. Even
 * if someone bypassed this component entirely, every API call the page
 * makes would still 403 server-side.
 */
export function RequireRole({ roles, children }: RequireRoleProps) {
  const { isAuthenticated, role } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  if (role === null || !roles.includes(role)) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}