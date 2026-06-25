const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

export function getToken() {
  return localStorage.getItem("finpick-token");
}

export function setToken(token) {
  if (token) {
    localStorage.setItem("finpick-token", token);
  } else {
    localStorage.removeItem("finpick-token");
  }
}

export async function apiFetch(path, options = {}) {
  const token = getToken();
  const isFormData = options.body instanceof FormData;
  const headers = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(options.headers || {})
  };
  if (token) {
    headers.Authorization = `Token ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(data.detail || data.non_field_errors?.[0] || "요청을 처리하지 못했습니다.", response.status, data);
  }
  return data;
}
