import { existsSync } from "node:fs";
import type { ForgeConfig } from "../config.js";
import {
  type AIProvider,
  type ChatChunk,
  type ChatRequest,
  type CompletionRequest,
  type CompletionResult,
  ProviderUnavailableError,
} from "./types.js";
import { heuristicCompletion } from "./heuristic.js";

/**
 * LocalLlamaProvider — LLM OFFLINE via node-llama-cpp (llama.cpp).
 *
 * NAO e Ollama e NAO hospeda nada. Roda um GGUF pequeno direto na CPU do Mac.
 * A dependencia `node-llama-cpp` e OPCIONAL: se nao estiver instalada ou o
 * modelo nao existir, caimos de forma limpa para o motor heuristico no inline
 * e informamos o usuario no chat.
 */
export class LocalLlamaProvider implements AIProvider {
  readonly name = "local-llama";
  readonly offline = true;

  private session: unknown | null = null;
  private llamaModule: any = null;

  constructor(private readonly cfg: ForgeConfig) {}

  async health(): Promise<{ ok: boolean; detail: string }> {
    const path = this.cfg.localLlama.modelPath;
    if (!path) return { ok: false, detail: "LOCAL_MODEL_PATH nao configurado." };
    if (!existsSync(path)) return { ok: false, detail: `Modelo nao encontrado: ${path}` };
    try {
      await this.ensureModule();
      return { ok: true, detail: `Modelo local pronto: ${path}` };
    } catch (e) {
      return { ok: false, detail: `node-llama-cpp indisponivel: ${(e as Error).message}` };
    }
  }

  private async ensureModule(): Promise<any> {
    if (this.llamaModule) return this.llamaModule;
    try {
      // import dinamico: dependencia opcional
      this.llamaModule = await import("node-llama-cpp");
      return this.llamaModule;
    } catch {
      throw new ProviderUnavailableError(
        "node-llama-cpp nao esta instalado.",
        "Rode: npm install node-llama-cpp --workspace @forgemind/core (precisa de internet uma vez).",
      );
    }
  }

  private async ensureSession(): Promise<any> {
    if (this.session) return this.session;
    const path = this.cfg.localLlama.modelPath;
    if (!path || !existsSync(path)) {
      throw new ProviderUnavailableError(
        "Modelo GGUF local nao encontrado.",
        "Baixe um GGUF pequeno para ./models/ e ajuste LOCAL_MODEL_PATH (ou o provider em Configuracoes).",
      );
    }
    const mod = await this.ensureModule();
    const llama = await mod.getLlama();
    const model = await llama.loadModel({ modelPath: path });
    const context = await model.createContext({
      contextSize: this.cfg.localLlama.contextSize,
      threads: this.cfg.localLlama.threads,
    });
    this.session = new mod.LlamaChatSession({ contextSequence: context.getSequence() });
    return this.session;
  }

  async *chat(req: ChatRequest): AsyncIterable<ChatChunk> {
    let session: any;
    try {
      session = await this.ensureSession();
    } catch (e) {
      const err = e as ProviderUnavailableError;
      yield {
        delta: `[local-llama indisponivel] ${err.message}${err.suggestion ? "\n\nSugestao: " + err.suggestion : ""}`,
        done: false,
      };
      yield { delta: "", done: true };
      return;
    }

    const prompt = buildPrompt(req);
    const chunks: string[] = [];
    await session.prompt(prompt, {
      temperature: req.temperature ?? 0.3,
      maxTokens: req.maxTokens ?? 512,
      signal: req.signal,
      onTextChunk: (t: string) => chunks.push(t),
    });
    for (const c of chunks) yield { delta: c, done: false };
    yield { delta: "", done: true };
  }

  async complete(req: CompletionRequest): Promise<CompletionResult> {
    // Para inline preferimos latencia baixa; se o modelo nao estiver pronto,
    // usamos o motor heuristico (rapido) em vez de travar o editor.
    try {
      await this.ensureSession();
    } catch {
      return heuristicCompletion(req);
    }
    // MVP: mantemos o inline heuristico mesmo com modelo carregado, para nao
    // sobrecarregar o Mac Intel a cada tecla. Chat usa o modelo; inline e leve.
    return heuristicCompletion(req);
  }
}

function buildPrompt(req: ChatRequest): string {
  const sys =
    req.messages.find((m) => m.role === "system")?.content ??
    "Voce e o ForgeMind, um assistente de desenvolvimento local. Responda em portugues, de forma tecnica e direta.";
  const history = req.messages
    .filter((m) => m.role !== "system")
    .map((m) => `${m.role === "user" ? "Usuario" : "ForgeMind"}: ${m.content}`)
    .join("\n");
  const ctx = req.context ? `\n\nContexto do projeto:\n${req.context}\n` : "";
  return `${sys}${ctx}\n\n${history}\nForgeMind:`;
}
