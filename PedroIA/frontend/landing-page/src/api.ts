import { API_URL } from "./config";

export interface AuthResult {
  access_token: string;
  email: string;
  display_name: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

async function req<T>(path: string, body?: unknown, token?: string): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(API_URL + path, {
    method: body ? "POST" : "GET",
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : {};
  if (!res.ok) {
    throw new Error(data.detail || `Erro ${res.status}`);
  }
  return data as T;
}

export const api = {
  register: (email: string, password: string, display_name: string) =>
    req<AuthResult>("/api/v1/auth/register", { email, password, display_name }),

  login: (email: string, password: string) =>
    req<AuthResult>("/api/v1/auth/login", { email, password }),

  chat: (messages: ChatMessage[], token: string, sessionId?: string) =>
    req<{ content: string; provider: string; model: string }>(
      "/api/v1/chat",
      { messages, mode: "auto", session_id: sessionId },
      token
    ),
};
