/**
 * PedroIA — Backend blindado
 * -------------------------------------------------------------
 * Um proxy fino e seguro entre a extensão do VS Code e a API da Anthropic (Claude).
 *
 * Por que existe:
 *  - A sua chave da Anthropic (ANTHROPIC_API_KEY) fica SÓ no servidor, nunca na extensão.
 *  - Rate limiting: evita que alguém torre a sua fatura de tokens.
 *  - Trava de segurança: em produção o servidor se RECUSA a subir sem API_KEYS
 *    (as chaves de acesso que os usuários da extensão precisam enviar).
 */

import express, { type Request, type Response, type NextFunction } from "express";
import cors from "cors";
import rateLimit from "express-rate-limit";
import Anthropic from "@anthropic-ai/sdk";

// ----------------------------------------------------------------------------
// Configuração via variáveis de ambiente
// ----------------------------------------------------------------------------
const PORT = Number(process.env.PORT || 8787);
const NODE_ENV = process.env.NODE_ENV || "development";
const IS_PROD = NODE_ENV === "production";

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY || "";
const MODEL = process.env.PEDROIA_MODEL || "claude-opus-5";
const RATE_LIMIT_MAX = Number(process.env.RATE_LIMIT_MAX || 3); // req por janela / IP
const RATE_LIMIT_WINDOW_MS = Number(process.env.RATE_LIMIT_WINDOW_MS || 60_000);
const MAX_TOKENS = Number(process.env.PEDROIA_MAX_TOKENS || 4096);

// API_KEYS = lista de chaves de acesso (separadas por vírgula) que os clientes
// da extensão devem enviar no header "x-pedroia-key". Isso protege o seu backend.
const API_KEYS = (process.env.API_KEYS || "")
  .split(",")
  .map((k) => k.trim())
  .filter(Boolean);

// ----------------------------------------------------------------------------
// TRAVA DE SEGURANÇA — não sobe em produção sem proteção
// ----------------------------------------------------------------------------
if (!ANTHROPIC_API_KEY) {
  console.error("❌ ANTHROPIC_API_KEY não definida. Configure a chave da Anthropic.");
  process.exit(1);
}
if (IS_PROD && API_KEYS.length === 0) {
  console.error(
    "❌ Recusando subir em produção sem API_KEYS.\n" +
      "   Defina API_KEYS (chaves de acesso da extensão) para não deixar um\n" +
      "   servidor aberto pagando IA para qualquer um da internet.\n" +
      "   Ex.: API_KEYS=chave-secreta-1,chave-secreta-2"
  );
  process.exit(1);
}

const anthropic = new Anthropic({ apiKey: ANTHROPIC_API_KEY });

// ----------------------------------------------------------------------------
// App
// ----------------------------------------------------------------------------
const app = express();
app.use(express.json({ limit: "1mb" }));
app.use(cors({ origin: "*", methods: ["GET", "POST"] }));
app.set("trust proxy", 1); // atrás do proxy do Render

// Rate limiting global (por IP)
const limiter = rateLimit({
  windowMs: RATE_LIMIT_WINDOW_MS,
  max: RATE_LIMIT_MAX,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "rate_limited", message: "Muitas requisições. Tente novamente em instantes." },
});

// Autenticação por chave de acesso da extensão
function requireKey(req: Request, res: Response, next: NextFunction) {
  if (API_KEYS.length === 0) return next(); // dev: sem chaves configuradas
  const provided = String(req.header("x-pedroia-key") || "");
  if (!provided || !API_KEYS.includes(provided)) {
    return res.status(401).json({ error: "unauthorized", message: "Chave de acesso inválida." });
  }
  next();
}

// ----------------------------------------------------------------------------
// Rotas
// ----------------------------------------------------------------------------

// Healthcheck (usado pelo Render e pela extensão para testar a conexão)
app.get("/health", (_req, res) => {
  res.json({ ok: true, service: "pedroia-backend", model: MODEL, env: NODE_ENV });
});

/**
 * POST /v1/chat
 * Body: { messages: [{role, content}], system?: string }
 * Retorna SSE (stream) com os pedaços de texto da resposta do Claude.
 */
app.post("/v1/chat", limiter, requireKey, async (req: Request, res: Response) => {
  const { messages, system } = req.body ?? {};
  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: "bad_request", message: "messages é obrigatório." });
  }

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.flushHeaders?.();

  const send = (event: string, data: unknown) =>
    res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);

  try {
    const stream = anthropic.messages.stream({
      model: MODEL,
      max_tokens: MAX_TOKENS,
      system:
        system ??
        "Você é o PedroIA, um engenheiro de software sênior integrado ao VS Code. " +
          "Responda de forma direta, prática e em português do Brasil. Ao mostrar código, " +
          "use blocos de código com a linguagem correta.",
      messages,
    });

    stream.on("text", (delta) => send("delta", { text: delta }));
    const final = await stream.finalMessage();
    send("done", { stop_reason: final.stop_reason, usage: final.usage });
    res.end();
  } catch (err: any) {
    const status = err?.status ?? 500;
    send("error", { status, message: err?.message ?? "Erro interno." });
    res.end();
  }
});

/**
 * POST /v1/complete  (autocomplete estilo Copilot)
 * Body: { prefix: string, suffix?: string, language?: string }
 * Retorna JSON: { completion: string } — o trecho a inserir no cursor.
 */
app.post("/v1/complete", limiter, requireKey, async (req: Request, res: Response) => {
  const { prefix, suffix = "", language = "plaintext" } = req.body ?? {};
  if (typeof prefix !== "string" || prefix.length === 0) {
    return res.status(400).json({ error: "bad_request", message: "prefix é obrigatório." });
  }

  try {
    const msg = await anthropic.messages.create({
      model: MODEL,
      max_tokens: 256,
      system:
        "Você é um motor de autocomplete de código, como o GitHub Copilot. " +
        "Complete o código a partir do CURSOR. Responda APENAS com o texto a inserir, " +
        "sem markdown, sem cercas de código, sem explicação. Continue no mesmo estilo e indentação.",
      messages: [
        {
          role: "user",
          content:
            `Linguagem: ${language}\n` +
            `<antes-do-cursor>\n${prefix}\n</antes-do-cursor>\n` +
            `<depois-do-cursor>\n${suffix}\n</depois-do-cursor>\n\n` +
            "Retorne SOMENTE o código que deve ser inserido no cursor:",
        },
      ],
    });

    const first = msg.content.find((b) => b.type === "text");
    let completion = first && "text" in first ? first.text : "";
    // Remove cercas de código caso o modelo insista em usá-las.
    completion = completion.replace(/^```[a-zA-Z0-9]*\n?/, "").replace(/\n?```$/, "");
    res.json({ completion });
  } catch (err: any) {
    const status = err?.status ?? 500;
    res.status(status).json({ error: "upstream", message: err?.message ?? "Erro interno." });
  }
});

app.listen(PORT, () => {
  console.log(`✅ PedroIA backend rodando na porta ${PORT} (${NODE_ENV})`);
  console.log(`   Modelo: ${MODEL} | Rate limit: ${RATE_LIMIT_MAX}/${RATE_LIMIT_WINDOW_MS}ms`);
  console.log(`   Proteção API_KEYS: ${API_KEYS.length > 0 ? "ATIVA" : "desativada (dev)"}`);
});
