const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  token?: string | null;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, token } = options;

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) {
    return undefined as T;
  }

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    // Our backend's standardized error shape is {"error": {"code", "message"}}.
    // Falls back gracefully for FastAPI's own 422 validation errors, which
    // use a different shape ({"detail": [...]}).
    if (data?.error) {
      throw new ApiError(data.error.code, data.error.message, res.status);
    }
    const fallbackMessage = data?.detail
      ? JSON.stringify(data.detail)
      : "Something went wrong";
    throw new ApiError("UNKNOWN_ERROR", fallbackMessage, res.status);
  }

  return data as T;
}