export interface AccessTokenClaims {
  sub: string;
  role: "student" | "staff" | "admin";
  username: string;
  exp: number;
  type: "access";
}

/**
 * Reads the (unencrypted, base64) payload of a JWT purely to drive UI
 * state — e.g. showing/hiding the "Manage Menu" link. This is NOT a
 * security boundary: the signature is never verified client-side, so this
 * must never be trusted for anything the backend doesn't independently
 * re-check. Every real permission check still happens server-side via
 * require_role — this only controls what's convenient to show or hide.
 */
export function decodeAccessToken(token: string): AccessTokenClaims | null {
  try {
    const payload = token.split(".")[1];
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(base64);
    return JSON.parse(json) as AccessTokenClaims;
  } catch {
    return null;
  }
}