import { geminiApiKey, type ForgeConfig } from "../config.js";
import { existsSync } from "node:fs";
import type { AIProvider, ChatChunk, ChatRequest, CompletionRequest, CompletionResult } from "./types.js";
import { GeminiProvider } from "./gemini.js";
import { LocalLlamaProvider } from "./local-llama.js";
import { HeuristicProvider } from "./heuristic.js";

/**
 * HybridProvider — o melhor dos dois mundos (PDF item 3/14/27):
 *   • CHAT   -> Gemini quando ha chave/internet; senao local-llama; senao heuristico.
 *   • INLINE -> SEMPRE local (local-llama FIM se houver modelo, senao heuristico),
 *               porque chamar API externa a cada tecla e caro e lento.
 *
 * Assim voce tem conversa forte (nuvem) e Ghost Text rapido e privado (local).
 */
export class HybridProvider implements AIProvider {
  readonly name = "hybrid";

  private readonly chatProvider: AIProvider;
  private readonly inlineProvider: AIProvider;

  constructor(cfg: ForgeConfig) {
    const hasKey = !!geminiApiKey();
    const hasModel = !!cfg.localLlama.modelPath && existsSync(cfg.localLlama.modelPath);

    this.chatProvider = hasKey
      ? new GeminiProvider(cfg)
      : hasModel
        ? new LocalLlamaProvider(cfg)
        : new HeuristicProvider();

    this.inlineProvider = hasModel ? new LocalLlamaProvider(cfg) : new HeuristicProvider();
  }

  /** offline apenas se o chat nao depender da nuvem. */
  get offline(): boolean {
    return this.chatProvider.offline;
  }

  async health(): Promise<{ ok: boolean; detail: string }> {
    const [chat, inline] = await Promise.all([this.chatProvider.health(), this.inlineProvider.health()]);
    return {
      ok: chat.ok || inline.ok,
      detail: `chat=${this.chatProvider.name} (${chat.ok ? "ok" : chat.detail}); inline=${this.inlineProvider.name} (${inline.ok ? "ok" : inline.detail})`,
    };
  }

  chat(req: ChatRequest): AsyncIterable<ChatChunk> {
    return this.chatProvider.chat(req);
  }

  complete(req: CompletionRequest): Promise<CompletionResult> {
    return this.inlineProvider.complete(req);
  }
}
