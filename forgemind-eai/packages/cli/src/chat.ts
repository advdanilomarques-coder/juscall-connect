import * as readline from "node:readline";
import { stdin as input, stdout as output } from "node:process";
import {
  createProvider,
  loadConfig,
  openDatabase,
  MemoryStore,
  retrieveContext,
  projectId,
  indexProject,
  runHealth,
  type ChatMessage,
} from "@forgemind/core";
import { aiLabel, banner, brand, hr, youPrompt } from "./ui.js";

const SYSTEM: ChatMessage = {
  role: "system",
  content:
    "Voce e o ForgeMind, uma IA pessoal de desenvolvimento e conhecimento geral, rodando LOCAL e OFFLINE na maquina do usuario. Responda em portugues, tecnica e diretamente. Compreenda antes de sugerir. Nunca invente APIs, comandos ou bibliotecas.",
};

/**
 * REPL de conversa estilo Claude Code — 100% no terminal, offline.
 * Conversa natural + comandos com barra. Streaming de tokens.
 */
export async function startChat(): Promise<void> {
  const cfg = loadConfig();
  const db = openDatabase(cfg);
  const memory = new MemoryStore(db);
  const provider = createProvider(cfg);
  const health = await provider.health();
  const site = `http://${cfg.host}:${cfg.port}`;
  const cwd = process.cwd();

  console.log(banner(cfg.provider, provider.offline, site));
  if (!health.ok) {
    console.log(brand.warn(`\n! ${health.detail}`));
    if (cfg.provider !== "heuristic") {
      console.log(brand.dim("  (usando fallback; ligue um modelo em /config ou rode: forgemind model:pull)\n"));
    }
  }
  console.log();

  const conversation = memory.createConversation("Terminal " + new Date().toLocaleString());
  const history: ChatMessage[] = [SYSTEM];

  const rl = readline.createInterface({ input, output, prompt: youPrompt() });
  rl.prompt();

  rl.on("line", async (raw) => {
    const line = raw.trim();
    if (!line) return rl.prompt();

    // ---- comandos ----
    if (line.startsWith("/") || line.toLowerCase() === "localhost") {
      const handled = await handleCommand(line, { cfg, db, memory, site, cwd, rl });
      if (handled === "exit") {
        rl.close();
        return;
      }
      if (handled) return rl.prompt();
    }

    // ---- conversa ----
    memory.addMessage(conversation.id, "user", line);
    history.push({ role: "user", content: line });

    let context: string | undefined;
    try {
      context = retrieveContext(db, cwd, line) || undefined;
    } catch {
      context = undefined;
    }

    process.stdout.write("\n" + aiLabel() + "\n");
    const controller = new AbortController();
    const onSigint = () => controller.abort();
    process.once("SIGINT", onSigint);

    let full = "";
    try {
      for await (const chunk of provider.chat({ messages: history, context, signal: controller.signal })) {
        if (chunk.delta) {
          full += chunk.delta;
          process.stdout.write(chunk.delta);
        }
        if (chunk.done) break;
      }
    } catch (e) {
      process.stdout.write(brand.err(`\n[erro] ${(e as Error).message}\n`));
    }
    process.removeListener("SIGINT", onSigint);
    memory.addMessage(conversation.id, "assistant", full);
    history.push({ role: "assistant", content: full });
    process.stdout.write("\n\n" + hr() + "\n");
    rl.prompt();
  });

  rl.on("close", () => {
    console.log(brand.dim("\nate a proxima. (ForgeMind offline)\n"));
    process.exit(0);
  });
}

interface Ctx {
  cfg: ReturnType<typeof loadConfig>;
  db: ReturnType<typeof openDatabase>;
  memory: MemoryStore;
  site: string;
  cwd: string;
  rl: readline.Interface;
}

async function handleCommand(line: string, ctx: Ctx): Promise<boolean | "exit"> {
  const [cmd, ...rest] = line.toLowerCase().replace(/^\//, "").split(/\s+/);
  const arg = rest.join(" ");

  switch (cmd) {
    case "help":
      console.log(helpText());
      return true;
    case "site":
    case "localhost":
    case "url":
      console.log(
        "\n" +
          brand.primary("◆ Seu site ForgeMind (local, so seu):") +
          "\n  " +
          brand.you(ctx.site) +
          "\n" +
          brand.dim("  abra no navegador para conversar por la. (rode `forgemind start` se ainda nao subiu)\n"),
      );
      return true;
    case "health":
    case "doctor": {
      const r = await runHealth(ctx.cfg, ctx.db);
      console.log("\n" + brand.primary("◆ Saude do sistema:"));
      for (const c of r.checks) {
        console.log(`  ${c.ok ? brand.ok("✔") : brand.err("✘")} ${c.name}: ${brand.dim(c.detail)}`);
      }
      console.log();
      return true;
    }
    case "index": {
      const root = arg || ctx.cwd;
      console.log(brand.dim(`\nindexando ${root} ...`));
      const s = indexProject(ctx.db, root);
      console.log(brand.ok(`✔ ${s.files} arquivos, ${s.symbols} simbolos (${s.skipped} ignorados)\n`));
      return true;
    }
    case "memory": {
      const items = arg ? ctx.memory.searchMemory(arg) : ctx.memory.listMemory(undefined, 10);
      console.log("\n" + brand.primary("◆ Memoria:"));
      if (items.length === 0) console.log(brand.dim("  (vazia)"));
      for (const m of items) console.log(`  ${brand.accent("#" + m.id)} ${brand.dim(m.kind)} ${m.value.slice(0, 80)}`);
      console.log();
      return true;
    }
    case "provider":
      console.log(`\n  provider atual: ${brand.accent(ctx.cfg.provider)} — troque em ${ctx.site} (/config)\n`);
      return true;
    case "clear":
      console.clear();
      return true;
    case "exit":
    case "quit":
    case "q":
      return "exit";
    default:
      console.log(brand.warn(`\ncomando desconhecido: /${cmd} — veja /help\n`));
      return true;
  }
}

function helpText(): string {
  const c = (s: string) => brand.accent(s);
  return [
    "",
    brand.primary("◆ Comandos"),
    `  ${c("/site")} ou ${c("localhost")}   mostra a URL do seu site local`,
    `  ${c("/health")}              diagnostico do sistema`,
    `  ${c("/index [caminho]")}     indexa o projeto (padrao: pasta atual)`,
    `  ${c("/memory [busca]")}      lista/pesquisa memoria`,
    `  ${c("/provider")}            mostra o cerebro atual`,
    `  ${c("/clear")}               limpa a tela`,
    `  ${c("/exit")}                sair`,
    brand.dim("  (Ctrl+C durante a resposta cancela a geracao)"),
    "",
  ].join("\n");
}
