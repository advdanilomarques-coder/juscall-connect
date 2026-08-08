import * as vscode from "vscode";
import * as http from "http";
import * as https from "https";
import { URL } from "url";

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  mode?: "auto" | "cloud" | "local";
  context?: ProjectContext;
  session_id?: string;
}

export interface ChatResponse {
  content: string;
  model: string;
  provider: string;
  mode: string;
}

export interface CompletionRequest {
  prefix: string;
  suffix: string;
  language: string;
  file_path: string;
  mode?: "auto" | "cloud" | "local";
}

export interface CompletionResponse {
  completion: string;
  model: string;
}

export interface ProjectContext {
  file_path?: string;
  language?: string;
  selection?: string;
  diagnostics?: string[];
  open_files?: string[];
  workspace_name?: string;
}

/**
 * Thin HTTP client for the PedroIA backend (FastAPI).
 * Uses the Node http/https modules so the extension has zero runtime deps.
 */
export class PedroIAClient {
  private get config() {
    return vscode.workspace.getConfiguration("cleancode");
  }

  private get baseUrl(): string {
    return (this.config.get<string>("backendUrl") || "http://127.0.0.1:8000").replace(/\/+$/, "");
  }

  private get apiKey(): string {
    return this.config.get<string>("apiKey") || "";
  }

  async chat(req: ChatRequest): Promise<ChatResponse> {
    return this.post<ChatResponse>("/api/v1/chat", req);
  }

  async complete(req: CompletionRequest): Promise<CompletionResponse> {
    return this.post<CompletionResponse>("/api/v1/complete", req);
  }

  async health(): Promise<{ status: string; online: boolean }> {
    return this.get<{ status: string; online: boolean }>("/api/v1/health");
  }

  private get<T>(path: string): Promise<T> {
    return this.request<T>("GET", path);
  }

  private post<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>("POST", path, body);
  }

  private request<T>(method: string, path: string, body?: unknown): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      let url: URL;
      try {
        url = new URL(this.baseUrl + path);
      } catch (e) {
        return reject(new Error(`URL de backend inválida: ${this.baseUrl}`));
      }
      const payload = body ? JSON.stringify(body) : undefined;
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        Accept: "application/json",
      };
      if (payload) {
        headers["Content-Length"] = Buffer.byteLength(payload).toString();
      }
      if (this.apiKey) {
        headers["Authorization"] = `Bearer ${this.apiKey}`;
      }

      const transport = url.protocol === "https:" ? https : http;
      const options: http.RequestOptions = {
        method,
        hostname: url.hostname,
        port: url.port || (url.protocol === "https:" ? 443 : 80),
        path: url.pathname + url.search,
        headers,
        timeout: 120000,
      };

      const req = transport.request(options, (res) => {
        const chunks: Buffer[] = [];
        res.on("data", (c) => chunks.push(c));
        res.on("end", () => {
          const raw = Buffer.concat(chunks).toString("utf8");
          const status = res.statusCode || 0;
          if (status >= 200 && status < 300) {
            try {
              resolve(raw ? (JSON.parse(raw) as T) : ({} as T));
            } catch (e) {
              reject(new Error(`Resposta inválida do backend: ${raw.slice(0, 200)}`));
            }
          } else {
            reject(new Error(`Backend retornou ${status}: ${raw.slice(0, 300)}`));
          }
        });
      });

      req.on("timeout", () => req.destroy(new Error("Tempo limite ao contatar o backend do PedroIA.")));
      req.on("error", (err) =>
        reject(new Error(`Não foi possível contatar o servidor em ${this.baseUrl}. ${err.message}`))
      );

      if (payload) {
        req.write(payload);
      }
      req.end();
    });
  }
}
