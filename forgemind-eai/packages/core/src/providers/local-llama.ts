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
 * NAO e Ollama e NAO hospeda nada. Roda um GGUF direto na CPU do Mac.
 * Chat usa LlamaChatSession; inline usa FIM (infill) com orcamento curto,
 * timeout e fallback heuristico — para nunca travar o editor (PDF 24/25/31).
 * A dependencia `node-llama-cpp` e OPCIONAL.
 */
export class LocalLlamaProvider implements AIProvider {
  readonly name = "local-llama";
  readonly offline = true;

  private mod: any = null;
  private model: any = null;
  private chatSession: any | null = null;
  private completion: any | null = null;

  constructor(private readonly cfg: ForgeConfig) {}

  async health(): Promise<{ ok: boolean; detail: string }> {
    const path = this.cfg.localLlama.modelPath;
    if (!path) return { ok: false, detail: "LOCAL_MODEL_PATH nao configurado." };
    if (!existsSync(path)) return { ok: false, detail: `Modelo nao encontrado: ${path}` };
    try {
      await this.ensureModel();
      return { ok: true, detail: `Modelo local pronto: ${path}` };
    } catch (e) {
      return { ok: false, detail: `node-llama-cpp indisponivel: ${(e as Error).message}` };
    }
  }

  private async ensureModule(): Promise<any> {
    if (this.mod) return this.mod;
    try {
      this.mod = await import("node-llama-cpp");
      return this.mod;
    } catch {
      throw new ProviderUnavailableError(
        "node-llama-cpp nao esta instalado.",
        "Rode: npm install node-llama-cpp --workspace @forgemind/core (precisa de internet uma vez).",
      );
    }
  }

  private async ensureModel(): Promise<any> {
    if (this.model) return this.model;
    const path = this.cfg.localLlama.modelPath;
    if (!path || !existsSync(path)) {
      throw new ProviderUnavailableError(
        "Modelo GGUF local nao encontrado.",
        "Baixe com ./scripts/model-pull.sh e ajuste o caminho em /config.",
      );
    }
    const mod = await this.ensureModule();
    const llama = await mod.getLlama();
    this.model = await llama.loadModel({ modelPath: path });
    return this.model;
  }

  private async ensureChat(): Promise<any> {
    if (this.chatSession) return this.chatSession;
    const mod = await this.ensureModule();
    const model = await this.ensureModel();
    const context = await model.createContext({
      contextSize: this.cfg.localLlama.contextSize,
      threads: this.cfg.localLlama.threads,
    });
    this.chatSession = new mod.LlamaChatSession({ contextSequence: context.getSequence() });
    return this.chatSession;
  }

  private async ensureCompletion(): Promise<any> {
    if (this.completion) return this.completion;
    const mod = await this.ensureModule();
    const model = await this.ensureModel();
    const context = await model.createContext({
      contextSize: Math.min(this.cfg.localLlama.contextSize, 2048),
      threads: this.cfg.localLlama.threads,
    });
    // LlamaCompletion suporta infill (FIM) quando o modelo tem tokens de FIM.
    this.completion = new mod.LlamaCompletion({ contextSequence: context.getSequence() });
    return this.completion;
  }

  async *chat(req: ChatRequest): AsyncIterable<ChatChunk> {
    let session: any;
    try {
      session = await this.ensureChat();
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
    const level = req.level ?? "BALANCED";
    if (level === "OFF") return { text: "", confidence: 0, multiline: false };

    // Orcamento por nivel: leve para o Mac Intel.
    const budget = { LOW: 12, BALANCED: 40, HIGH: 96 }[level] ?? 40;
    const timeoutMs = { LOW: 2500, BALANCED: 4500, HIGH: 8000 }[level] ?? 4500;

    let completion: any;
    try {
      completion = await this.ensureCompletion();
    } catch {
      return heuristicCompletion(req); // modelo ainda nao pronto: nao trava o editor
    }

    const prefix = (req.context ? `/* Contexto:\n${req.context}\n*/\n` : "") + req.prefix;
    const ctl = new AbortController();
    const onAbort = () => ctl.abort();
    req.signal?.addEventListener("abort", onAbort);
    const timer = setTimeout(() => ctl.abort(), timeoutMs);

    try {
      const text: string = await completion.generateInfillCompletion(prefix, req.suffix, {
        maxTokens: budget,
        temperature: 0.1,
        signal: ctl.signal,
      });
      const cleaned = postProcess(text, level);
      if (!cleaned) return heuristicCompletion(req);
      return { text: cleaned, confidence: confidenceFor(cleaned), multiline: cleaned.includes("\n") };
    } catch {
      // timeout/cancelamento/modelo sem FIM: cai no heuristico
      return heuristicCompletion(req);
    } finally {
      clearTimeout(timer);
      req.signal?.removeEventListener("abort", onAbort);
    }
  }
}

function postProcess(text: string, level: string): string {
  let t = text.replace(/<\|[^|]*\|>/g, ""); // remove tokens especiais residuais
  if (level === "LOW") {
    // uma linha so
    const nl = t.indexOf("\n");
    if (nl >= 0) t = t.slice(0, nl);
  } else {
    // limita a blocos razoaveis
    const lines = t.split("\n").slice(0, level === "HIGH" ? 12 : 5);
    t = lines.join("\n");
  }
  return t.replace(/\s+$/, "");
}

function confidenceFor(text: string): number {
  // Heuristica simples: sugestoes muito curtas ou muito longas => menor confianca.
  const len = text.trim().length;
  if (len === 0) return 0;
  if (len < 2) return 0.3;
  if (len > 400) return 0.4;
  return 0.7;
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
