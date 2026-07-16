import { createContext, useContext, useState, type ReactNode } from "react";
import { apiRequest } from "../api/client";
import { decodeAccessToken } from "../utils/jwt";

interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface RegisterInput {
  full_name: string;
  username: string;
  email: string;
  password: string;
}

type Role = "student" | "staff" | "admin";

interface AuthContextValue {
  accessToken: string | null;
  isAuthenticated: boolean;
  role: Role | null;
  username: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (data: RegisterInput) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Tokens live in localStorage so a page refresh doesn't log the user out.
// Known tradeoff: localStorage is readable by any JS on the page (XSS
// exposure) in a way an httpOnly cookie wouldn't be. Accepted here because
// the backend issues Bearer tokens by design (see docs/api-contract.md),
// not cookies. Revisiting this is a Phase 2 security-hardening candidate,
// not a Day 5 concern — noting it so it isn't forgotten.
const ACCESS_TOKEN_KEY = "campusbites_access_token";
const REFRESH_TOKEN_KEY = "campusbites_refresh_token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(() =>
    localStorage.getItem(ACCESS_TOKEN_KEY)
  );

  function storeTokens(tokens: TokenPair) {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    setAccessToken(tokens.access_token);
  }

  function clearTokens() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setAccessToken(null);
  }

  async function login(username: string, password: string) {
    const tokens = await apiRequest<TokenPair>("/auth/login", {
      method: "POST",
      body: { username, password },
    });
    storeTokens(tokens);
  }

  async function register(data: RegisterInput) {
    await apiRequest("/auth/register", { method: "POST", body: data });
    // Registration does NOT log the user in — matches the backend contract
    // (register returns the created user, not tokens). RegisterPage sends
    // them to /login next.
  }

  async function logout() {
    const token = accessToken;
    clearTokens(); // clear client-side state immediately, regardless of network outcome
    if (token) {
      try {
        await apiRequest("/auth/logout", { method: "POST", token });
      } catch {
        // Already logged out client-side; a failed network call here
        // shouldn't block the user from being logged out in the UI.
      }
    }
  }

  const claims = accessToken ? decodeAccessToken(accessToken) : null;

  const value: AuthContextValue = {
    accessToken,
    isAuthenticated: accessToken !== null,
    role: claims?.role ?? null,
    username: claims?.username ?? null,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}