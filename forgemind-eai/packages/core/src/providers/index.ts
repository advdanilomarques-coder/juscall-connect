import type { ForgeConfig } from "../config.js";
import { HeuristicProvider } from "./heuristic.js";
import { LocalLlamaProvider } from "./local-llama.js";
import { GeminiProvider } from "./gemini.js";
import type { AIProvider } from "./types.js";

export * from "./types.js";
export { HeuristicProvider } from "./heuristic.js";
export { LocalLlamaProvider } from "./local-llama.js";
export { GeminiProvider } from "./gemini.js";

/**
 * Factory de provider (PDF item 4): o nome do modelo/fornecedor nao se espalha
 * pelo codigo — resolve-se por configuracao. Se o provider pedido nao existir,
 * caimos no heuristico (que sempre funciona, offline).
 */
export function createProvider(cfg: ForgeConfig): AIProvider {
  switch (cfg.provider) {
    case "gemini":
      return new GeminiProvider(cfg);
    case "local-llama":
      return new LocalLlamaProvider(cfg);
    case "heuristic":
    default:
      return new HeuristicProvider();
  }
}

/** Provider heuristico sempre disponivel para fallback de inline. */
export function fallbackProvider(): AIProvider {
  return new HeuristicProvider();
}
