import { geminiApiKey, type ForgeConfig } from "../config.js";
import {
  type AIProvider,
  type ChatChunk,
  type ChatRequest,
  type CompletionRequest,
  type CompletionResult,
  ProviderUnavailableError,
} from "./types.js";
import { heuristicCompletion } from "./heuristic.js";
import { redactSecrets } from "../redaction.js";

/**
 * GeminiProvider — provider ONLINE opcional (Google Gemini API).
 *
 * Desligado por padrao. A chamada ocorre SEMPRE no backend; a API key nunca
 * e exposta ao frontend nem gravada em config.json (PDF item 10/11).
 * Usa fetch nativo (Node 20+), sem SDK, para manter dependencias minimas.
 */
export class GeminiProvider implements AIProvider {
  readonly name = "gemini";
  readonly offline = false;

  constructor(private readonly cfg: ForgeConfig) {}

  private endpoint(stream: boolean): string {
    const model = this.cfg.gemini.model || "gemini-1.5-flash";
    const method = stream ? "streamGenerateContent" : "generateContent";
    return `https://generativelanguage.googleapis.com/v1beta/models/${model}:${method}`;
  }

  async health(): Promise<{ ok: boolean; detail: string }> {
    if (!geminiApiKey()) return { ok: false, detail: "GEMINI_API_KEY ausente (defina no ambiente do backend)." };
    return { ok: true, detail: `Gemini configurado (modelo ${this.cfg.gemini.model}). Requer internet.` };
  }

  async *chat(req: ChatRequest): AsyncIterable<ChatChunk> {
    const key = geminiApiKey();
    if (!key) {
      throw new ProviderUnavailableError(
        "GEMINI_API_KEY nao definida.",
        "Defina a variavel de ambiente GEMINI_API_KEY no backend e selecione o provider gemini.",
      );
    }
    const contents = req.messages
      .filter((m) => m.role !== "system")
      .map((m) => ({ role: m.role === "assistant" ? "model" : "user", parts: [{ text: m.content }] }));
    const sysText = req.messages.find((m) => m.role === "system")?.content;
    const body = {
      contents,
      ...(sysText || req.context
        ? { systemInstruction: { parts: [{ text: [sysText, req.context].filter(Boolean).join("\n\n") }] } }
        : {}),
      generationConfig: { temperature: req.temperature ?? 0.4, maxOutputTokens: req.maxTokens ?? 1024 },
    };

    const res = await fetch(`${this.endpoint(false)}?key=${encodeURIComponent(key)}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
      signal: req.signal,
    });
    if (!res.ok) {
      const detail = redactSecrets(await res.text());
      throw new ProviderUnavailableError(`Gemini retornou ${res.status}.`, detail.slice(0, 300));
    }
    const json: any = await res.json();
    const text: string = json?.candidates?.[0]?.content?.parts?.map((p: any) => p.text).join("") ?? "";
    // stream simples por palavra
    for (const w of text.split(/(\s+)/)) yield { delta: w, done: false };
    yield { delta: "", done: true };
  }

  async complete(req: CompletionRequest): Promise<CompletionResult> {
    // Inline com API externa a cada tecla e caro e lento; mantemos o inline
    // heuristico local mesmo com Gemini ativo (chat usa Gemini).
    return heuristicCompletion(req);
  }
}
