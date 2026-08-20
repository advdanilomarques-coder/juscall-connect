export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  /** Contexto de projeto ja selecionado/rankeado (nunca o projeto inteiro). */
  context?: string;
  temperature?: number;
  maxTokens?: number;
  signal?: AbortSignal;
}

export interface ChatChunk {
  delta: string;
  done: boolean;
}

export interface CompletionRequest {
  /** Texto antes do cursor. */
  prefix: string;
  /** Texto depois do cursor. */
  suffix: string;
  language: string;
  path?: string;
  /** Simbolos/contexto relevante do projeto. */
  context?: string;
  signal?: AbortSignal;
}

export interface CompletionResult {
  text: string;
  /** 0..1 — abaixo de min_confidence o Ghost Text nao aparece (PDF item 21). */
  confidence: number;
  multiline: boolean;
}

/** Contrato unico que desacopla o nucleo do fornecedor (PDF item 3/9). */
export interface AIProvider {
  readonly name: string;
  /** true se funciona sem internet. */
  readonly offline: boolean;
  /** Verifica se o provider esta pronto (modelo presente, key presente, etc). */
  health(): Promise<{ ok: boolean; detail: string }>;
  /** Chat com streaming. */
  chat(req: ChatRequest): AsyncIterable<ChatChunk>;
  /** Completion inline (Ghost Text). */
  complete(req: CompletionRequest): Promise<CompletionResult>;
}

export class ProviderUnavailableError extends Error {
  constructor(
    message: string,
    public readonly suggestion?: string,
  ) {
    super(message);
    this.name = "ProviderUnavailableError";
  }
}
