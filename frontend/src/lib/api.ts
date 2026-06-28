export const API_PREFIX = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export const authFetch = async (url: string, options: RequestInit = {}): Promise<Response> => {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  return fetch(url, { ...options, headers });
};

export const apiGet = async <T>(path: string): Promise<T> => {
  const res = await authFetch(`${API_PREFIX}${path}`);
  if (!res.ok) throw new ApiError(`Request failed: ${res.statusText}`, res.status);
  return res.json();
};

export const apiPost = async <T>(path: string, body?: unknown): Promise<T> => {
  const res = await authFetch(`${API_PREFIX}${path}`, {
    method: 'POST',
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new ApiError(`Request failed: ${res.statusText}`, res.status);
  return res.json();
};

export const apiPut = async <T>(path: string, body: unknown): Promise<T> => {
  const res = await authFetch(`${API_PREFIX}${path}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new ApiError(`Request failed: ${res.statusText}`, res.status);
  return res.json();
};

export const apiDelete = async (path: string): Promise<void> => {
  const res = await authFetch(`${API_PREFIX}${path}`, { method: 'DELETE' });
  if (!res.ok) throw new ApiError(`Request failed: ${res.statusText}`, res.status);
};
