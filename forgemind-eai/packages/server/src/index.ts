import { existsSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import Fastify from "fastify";
import cors from "@fastify/cors";
import fastifyStatic from "@fastify/static";
import {
  loadEnvFiles,
  saveConfig,
  redactObject,
  runHealth,
  indexProject,
  retrieveContext,
  retrieveFileContext,
  terminalGhost,
  explainCommand,
  isDangerous,
  configureLogger,
  logger,
  type ChatMessage,
} from "@forgemind/core";
import { ServerState } from "./state.js";

loadEnvFiles(); // ./.env e ~/.forgemind/.env (Gemini/local-llama de qualquer lugar)
const state = new ServerState();
configureLogger({ file: logger.fileIn(state.config.home) });

const app = Fastify({ logger: false, bodyLimit: 5 * 1024 * 1024 });

// CORS: apenas origens locais (o app nunca e hospedado publicamente).
await app.register(cors, {
  origin: [/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/],
});

// Hardening (defesa contra CSRF / DNS-rebinding em servico localhost):
//  - rejeita Origin de fora do localhost (CORS so ajusta headers de resposta;
//    aqui bloqueamos a requisicao de fato antes de executar qualquer efeito);
//  - valida o Host para impedir rebinding via dominio que resolve p/ 127.0.0.1.
const LOCAL_RE = /^(localhost|127\.0\.0\.1)(:\d+)?$/;
app.addHook("onRequest", async (req, reply) => {
  const origin = req.headers.origin;
  if (origin) {
    try {
      if (!LOCAL_RE.test(new URL(origin).host)) return reply.code(403).send({ error: "origem nao permitida" });
    } catch {
      return reply.code(403).send({ error: "origem invalida" });
    }
  }
  const host = req.headers.host;
  if (host && !LOCAL_RE.test(host)) return reply.code(403).send({ error: "host nao permitido" });
});

// Servir o site (build do web) se existir, para que o localhost mostre "seu site".
const here = dirname(fileURLToPath(import.meta.url));
const webDist = resolve(here, "../../web/dist");
if (existsSync(join(webDist, "index.html"))) {
  await app.register(fastifyStatic, { root: webDist, prefix: "/" });
}

// -------------------- Health --------------------
app.get("/api/health", async () => {
  const report = await runHealth(state.config, state.db);
  return report;
});

app.get("/api/info", async () => ({
  name: "ForgeMind EAI",
  version: "0.1.0",
  provider: state.config.provider,
  offline: state.getProvider().offline,
  site: `http://${state.config.host}:${state.config.port}`,
}));

// -------------------- Config (/config) --------------------
app.get("/api/config", async () => {
  // redactObject garante que nenhum segredo vaze mesmo que apareca.
  const { home, ...rest } = state.config;
  return redactObject(rest);
});

app.put("/api/config", async (req) => {
  const body = (req.body ?? {}) as Record<string, unknown>;
  const next = saveConfig(body);
  state.reloadConfig(next);
  const { home, ...rest } = next;
  return redactObject(rest);
});

// -------------------- Chat (SSE streaming) --------------------
app.post("/api/chat", async (req, reply) => {
  const body = req.body as { conversationId?: number; messages?: ChatMessage[]; projectRoot?: string };
  const messages = body.messages ?? [];
  const userText = [...messages].reverse().find((m) => m.role === "user")?.content ?? "";

  // Context Engine: recupera so o relevante (nunca o projeto inteiro).
  let context: string | undefined;
  if (body.projectRoot && userText) {
    try {
      context = retrieveContext(state.db, body.projectRoot, userText, { maxSymbols: 32, maxChars: 3200 }) || undefined;
    } catch {
      context = undefined;
    }
  }

  // Persistir a mensagem do usuario, se houver conversa.
  if (body.conversationId && userText) {
    try {
      state.memory.addMessage(body.conversationId, "user", userText);
    } catch {
      /* conversa pode nao existir ainda */
    }
  }

  reply.raw.writeHead(200, {
    "content-type": "text/event-stream",
    "cache-control": "no-cache",
    connection: "keep-alive",
  });

  const controller = new AbortController();
  req.raw.on("close", () => controller.abort());

  const provider = state.getProvider();
  let full = "";
  try {
    for await (const chunk of provider.chat({ messages, context, signal: controller.signal })) {
      if (chunk.delta) {
        full += chunk.delta;
        reply.raw.write(`data: ${JSON.stringify({ delta: chunk.delta })}\n\n`);
      }
      if (chunk.done) break;
    }
  } catch (e) {
    reply.raw.write(`data: ${JSON.stringify({ error: (e as Error).message })}\n\n`);
  }

  if (body.conversationId && full) {
    try {
      state.memory.addMessage(body.conversationId, "assistant", full);
    } catch {
      /* ignore */
    }
  }
  reply.raw.write("data: [DONE]\n\n");
  reply.raw.end();
});

// -------------------- Ghost Text (inline) --------------------
app.post("/api/complete", async (req) => {
  const b = req.body as {
    prefix: string;
    suffix: string;
    language: string;
    path?: string;
    projectRoot?: string;
  };
  const level = state.config.inline.level;
  if (level === "OFF") return { text: "", confidence: 0, multiline: false };

  // Contexto CRUZADO: simbolos do arquivo atual + dos modulos que ele importa.
  let context: string | undefined;
  if (b.projectRoot) {
    const word = (b.prefix.match(/[A-Za-z_$][A-Za-z0-9_$]*$/) ?? [""])[0];
    try {
      if (b.path) {
        const rel = relative(b.projectRoot, b.path);
        context = retrieveFileContext(state.db, b.projectRoot, rel, word, { maxSymbols: 16 }) || undefined;
      } else if (word.length >= 3) {
        context = retrieveContext(state.db, b.projectRoot, word, { maxSymbols: 30 }) || undefined;
      }
    } catch {
      /* ignore */
    }
  }

  const request = {
    prefix: b.prefix ?? "",
    suffix: b.suffix ?? "",
    language: b.language ?? "plaintext",
    path: b.path,
    context,
    level,
  };

  // Cache (PDF item 25): reutiliza enquanto o contexto relevante nao muda.
  const cached = state.completionCache.get(request);
  if (cached) return cached;

  const result = await state.getProvider().complete(request);
  // Confidence gate (PDF item 21): abaixo do minimo, nao sugere.
  const gated =
    result.confidence < state.config.inline.minConfidence
      ? { text: "", confidence: result.confidence, multiline: false }
      : result;
  if (gated.text) state.completionCache.set(request, gated);
  return gated;
});

// -------------------- Terminal AI --------------------
app.post("/api/terminal/suggest", async (req) => {
  const b = req.body as { partial: string; cwd?: string; recent?: string[]; files?: string[] };
  const g = terminalGhost(b.partial ?? "", {
    cwd: b.cwd ?? process.cwd(),
    os: process.platform,
    recent: b.recent ?? [],
    files: b.files,
  });
  return g;
});

app.post("/api/terminal/explain", async (req) => {
  const b = req.body as { command: string };
  return { explanation: explainCommand(b.command ?? ""), dangerous: isDangerous(b.command ?? "") };
});

// -------------------- Conversas / historico --------------------
app.get("/api/conversations", async () => state.memory.listConversations());
app.post("/api/conversations", async (req) => {
  const b = (req.body ?? {}) as { title?: string };
  return state.memory.createConversation(b.title);
});
app.get("/api/conversations/:id/messages", async (req) => {
  const id = Number((req.params as { id: string }).id);
  return state.memory.getMessages(id);
});
app.delete("/api/conversations/:id", async (req) => {
  const id = Number((req.params as { id: string }).id);
  state.memory.deleteConversation(id);
  return { ok: true };
});

// -------------------- Memoria --------------------
app.get("/api/memory", async (req) => {
  const q = (req.query as { q?: string }).q ?? "";
  return q ? state.memory.searchMemory(q) : state.memory.listMemory();
});
app.post("/api/memory", async (req) => {
  const b = req.body as { value: string; scope?: string; kind?: string; key?: string };
  return state.memory.remember(b.value, b);
});
app.delete("/api/memory/:id", async (req) => {
  state.memory.forget(Number((req.params as { id: string }).id));
  return { ok: true };
});
app.get("/api/memory/export", async () => redactObject(state.memory.export()));

// -------------------- Indexacao de projeto --------------------
app.post("/api/index", async (req) => {
  const b = req.body as { root: string };
  const root = resolve(b.root);
  if (!existsSync(root)) return { error: "Diretorio nao encontrado." };
  return indexProject(state.db, root);
});

// -------------------- Fallback amigavel --------------------
// Se o site nao estiver compilado, "/" nao daria 404 cru: mostra instrucoes.
const siteBuilt = existsSync(join(webDist, "index.html"));
app.setNotFoundHandler((req, reply) => {
  const wantsHtml = (req.headers.accept ?? "").includes("text/html");
  if (wantsHtml && !siteBuilt) {
    reply.type("text/html").send(`<!doctype html><meta charset="utf-8">
<title>ForgeMind EAI</title>
<body style="font-family:system-ui;background:#0f1115;color:#e6e6e6;display:grid;place-items:center;height:100vh;margin:0">
<div style="max-width:520px;padding:2rem;border:1px solid #2a2f3a;border-radius:16px">
<h1 style="color:#FF7A1A;margin:0 0 .5rem">ForgeMind EAI</h1>
<p>O backend esta rodando, mas o <b>site ainda nao foi compilado</b>.</p>
<p>Rode no terminal, dentro da pasta do projeto:</p>
<pre style="background:#161a22;padding:1rem;border-radius:8px;overflow:auto">npm run build:web</pre>
<p>Depois reinicie o servidor e recarregue esta pagina.</p>
<p style="color:#8a94a6">API disponivel em <code>/api/health</code>, <code>/api/info</code>.</p>
</div></body>`);
    return;
  }
  reply.code(404).send({ message: `Rota ${req.method}:${req.url} nao encontrada`, statusCode: 404 });
});

// -------------------- Start --------------------
const port = state.config.port;
const host = state.config.host;
app
  .listen({ port, host })
  .then(() => {
    const url = `http://${host}:${port}`;
    logger.info(`ForgeMind server em ${url} (provider: ${state.config.provider})`);
    process.stdout.write(`\nForgeMind rodando: ${url}\n`);
  })
  .catch((e) => {
    logger.error("Falha ao iniciar servidor", { error: (e as Error).message });
    process.exit(1);
  });
