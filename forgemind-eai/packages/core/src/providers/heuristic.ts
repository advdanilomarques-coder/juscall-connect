import type {
  AIProvider,
  ChatChunk,
  ChatRequest,
  CompletionRequest,
  CompletionResult,
} from "./types.js";

/**
 * HeuristicProvider — 100% OFFLINE, sem modelo, sem download, sem internet.
 *
 * Nao e um LLM. E um motor deterministico que:
 *  - completa Ghost Text por analise sintatica leve (pares, indentacao, padroes
 *    da linguagem, simbolos do contexto);
 *  - responde chat com base de conhecimento local + acoes sobre a memoria/projeto.
 *
 * Objetivo (PDF item 27): ser UTIL de imediato num Mac Intel fraco, sem custo.
 * Para respostas de linguagem natural mais ricas, o usuario ativa `local-llama`.
 */
export class HeuristicProvider implements AIProvider {
  readonly name = "heuristic";
  readonly offline = true;

  async health(): Promise<{ ok: boolean; detail: string }> {
    return { ok: true, detail: "Motor heuristico offline pronto (sem modelo, sem internet)." };
  }

  async *chat(req: ChatRequest): AsyncIterable<ChatChunk> {
    const last = [...req.messages].reverse().find((m) => m.role === "user")?.content ?? "";
    const answer = this.answer(last, req.context);
    // stream por palavra para a UI parecer viva
    const words = answer.split(/(\s+)/);
    for (const w of words) {
      yield { delta: w, done: false };
    }
    yield { delta: "", done: true };
  }

  async complete(req: CompletionRequest): Promise<CompletionResult> {
    return heuristicCompletion(req);
  }

  private answer(input: string, context?: string): string {
    const q = input.toLowerCase().trim();
    const kb = KNOWLEDGE.find((k) => k.match.some((m) => q.includes(m)));
    const ctxNote = context
      ? "\n\n_(Contexto de projeto disponivel foi considerado.)_"
      : "";

    if (!input.trim()) {
      return "Manda a pergunta que eu ajudo. Estou em **modo offline (heuristico)** — sem internet e sem modelo. Para respostas de linguagem natural mais completas, ative o provider `local-llama` em Configuracoes.";
    }
    if (kb) return kb.answer + ctxNote;

    return [
      "Estou rodando em **modo heuristico offline** (sem LLM externo, sem internet).",
      "",
      "Nesse modo eu sou forte em: **Ghost Text/completions**, **sugestoes de terminal**, **indice do projeto**, **memoria/historico** e **diagnostico/saude**.",
      "",
      "Para uma resposta conversacional aprofundada sobre isso, ative um modelo local:",
      "1. Baixe um GGUF pequeno (uma vez, com internet) para `./models/`.",
      "2. Em Configuracoes, escolha o provider **local-llama** e aponte o caminho.",
      "",
      `Sua pergunta foi: _${input.trim()}_`,
    ].join("\n") + ctxNote;
  }
}

interface KBEntry {
  match: string[];
  answer: string;
}

const KNOWLEDGE: KBEntry[] = [
  {
    match: ["ollama"],
    answer:
      "O ForgeMind **nao usa Ollama** por decisao de projeto (Mac Intel + requisito offline sem dependencia pesada). O provider padrao e o `heuristic` (offline). Para um LLM local sem Ollama, use `local-llama` (node-llama-cpp com um GGUF pequeno).",
  },
  {
    match: ["offline", "internet", "sem rede"],
    answer:
      "Sim: o app roda **local e offline**. Memoria, historico, indice de projeto, terminal e health funcionam sem internet. So o provider `gemini` (opcional, desligado) exige rede.",
  },
  {
    match: ["gemini", "api key", "provider"],
    answer:
      "A arquitetura e plugavel: `heuristic` (offline, padrao), `local-llama` (offline, GGUF) e `gemini` (online, opcional). A chave do Gemini fica **so no backend**, via variavel de ambiente `GEMINI_API_KEY`, nunca no frontend nem no config.json.",
  },
  {
    match: ["git status", "git ", "commit"],
    answer:
      "Fluxo Git seguro: `git status` para ver o estado, `git add -p` para revisar por trecho, `git commit -m \"...\"`, `git push`. O Terminal AI do ForgeMind explica e sugere comandos, mas **nunca executa comandos perigosos automaticamente** (PDF item 30).",
  },
  {
    match: ["fastapi", "python backend"],
    answer:
      "Observacao de arquitetura: o PDF pedia FastAPI/Python, mas esta build usa **backend Node/TypeScript** para casar com seu ambiente Node 20/npm 10, um unico toolchain e inferencia local nativa (node-llama-cpp). A camada de provider continua agnostica.",
  },
];

// ---------------------------------------------------------------------------
// Ghost Text heuristico (compartilhado)
// ---------------------------------------------------------------------------

const PAIR: Record<string, string> = { "(": ")", "[": "]", "{": "}" };

export function heuristicCompletion(req: CompletionRequest): CompletionResult {
  const line = currentLine(req.prefix);
  const trimmed = line.trimEnd();
  const indent = line.match(/^\s*/)?.[0] ?? "";
  const lang = req.language.toLowerCase();

  // 1) Fechar pares abertos na linha
  const open = lastUnmatchedOpener(trimmed);
  if (open && !req.suffix.startsWith(PAIR[open]!)) {
    return { text: PAIR[open]!, confidence: 0.55, multiline: false };
  }

  // 2) Blocos que pedem corpo indentado
  if (/[:{]\s*$/.test(trimmed)) {
    const step = indentUnit(lang);
    return { text: "\n" + indent + step, confidence: 0.5, multiline: true };
  }

  // 3) Padroes por linguagem
  const byLang = languagePattern(trimmed, lang, indent);
  if (byLang) return byLang;

  // 4) Completar a partir de simbolos do contexto (identificador parcial)
  const word = trimmed.match(/[A-Za-z_$][A-Za-z0-9_$]*$/)?.[0] ?? "";
  if (word.length >= 3 && req.context) {
    const cand = symbolsFromContext(req.context)
      .filter((s) => s.startsWith(word) && s !== word)
      .sort((a, b) => a.length - b.length)[0];
    if (cand) {
      return { text: cand.slice(word.length), confidence: 0.45, multiline: false };
    }
  }

  return { text: "", confidence: 0, multiline: false };
}

function currentLine(prefix: string): string {
  const idx = prefix.lastIndexOf("\n");
  return idx === -1 ? prefix : prefix.slice(idx + 1);
}

function indentUnit(lang: string): string {
  if (lang === "python" || lang === "yaml") return "    ";
  return "  ";
}

function lastUnmatchedOpener(s: string): string | null {
  const stack: string[] = [];
  let inStr: string | null = null;
  for (const ch of s) {
    if (inStr) {
      if (ch === inStr) inStr = null;
      continue;
    }
    if (ch === '"' || ch === "'" || ch === "`") inStr = ch;
    else if (ch in PAIR) stack.push(ch);
    else if (ch === ")" || ch === "]" || ch === "}") stack.pop();
  }
  return stack.length ? stack[stack.length - 1]! : null;
}

function languagePattern(line: string, lang: string, indent: string): CompletionResult | null {
  if (["typescript", "javascript", "typescriptreact", "javascriptreact"].includes(lang)) {
    if (/^\s*(export\s+)?(async\s+)?function\s+\w+\s*\([^)]*$/.test(line)) return null;
    if (/\bconsole\.$/.test(line)) return { text: "log()", confidence: 0.5, multiline: false };
    if (/=>\s*$/.test(line)) return { text: " {\n" + indent + "  \n" + indent + "}", confidence: 0.45, multiline: true };
    if (/^\s*if\s*\($/.test(line)) return { text: ")", confidence: 0.4, multiline: false };
  }
  if (lang === "python") {
    if (/^\s*def\s+\w+\s*\([^)]*$/.test(line)) return null;
    if (/^\s*print$/.test(line)) return { text: "()", confidence: 0.5, multiline: false };
    if (/^\s*for\s+\w+\s+in\s+.+$/.test(line) && !line.endsWith(":"))
      return { text: ":", confidence: 0.45, multiline: false };
  }
  return null;
}

function symbolsFromContext(context: string): string[] {
  const set = new Set<string>();
  const re = /[A-Za-z_$][A-Za-z0-9_$]{2,}/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(context))) set.add(m[0]);
  return [...set];
}
