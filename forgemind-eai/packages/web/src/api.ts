export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface Info {
  name: string;
  version: string;
  provider: string;
  offline: boolean;
  site: string;
}

export interface HealthCheck {
  name: string;
  ok: boolean;
  detail: string;
}

export interface Config {
  provider: "heuristic" | "local-llama" | "gemini";
  host: string;
  port: number;
  theme: "light" | "dark" | "system";
  inline: { level: string; debounceMs: number; minConfidence: number };
  localLlama: { modelPath: string; contextSize: number; threads: number };
  gemini: { model: string };
}

export interface MemoryItem {
  id: number;
  scope: string;
  kind: string;
  key: string | null;
  value: string;
  created_at: string;
}

async function j<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const api = {
  info: () => j<Info>("/api/info"),
  health: () => j<{ ok: boolean; checks: HealthCheck[] }>("/api/health"),
  getConfig: () => j<Config>("/api/config"),
  putConfig: (patch: Partial<Config>) => j<Config>("/api/config", { method: "PUT", body: JSON.stringify(patch) }),
  memory: (q?: string) => j<MemoryItem[]>(`/api/memory${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  addMemory: (value: string) => j<MemoryItem>("/api/memory", { method: "POST", body: JSON.stringify({ value }) }),
  delMemory: (id: number) => j<{ ok: boolean }>(`/api/memory/${id}`, { method: "DELETE" }),

  /** Chat com streaming SSE. onDelta recebe cada pedaco de texto. */
  async chat(
    messages: ChatMessage[],
    onDelta: (t: string) => void,
    signal?: AbortSignal,
  ): Promise<void> {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ messages }),
      signal,
    });
    if (!res.body) throw new Error("sem corpo de resposta");
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let buf = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const parts = buf.split("\n\n");
      buf = parts.pop() ?? "";
      for (const p of parts) {
        const line = p.trim();
        if (!line.startsWith("data:")) continue;
        const data = line.slice(5).trim();
        if (data === "[DONE]") return;
        try {
          const obj = JSON.parse(data);
          if (obj.delta) onDelta(obj.delta);
          if (obj.error) onDelta(`\n[erro] ${obj.error}`);
        } catch {
          /* ignore keepalive */
        }
      }
    }
  },
};
