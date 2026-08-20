#!/usr/bin/env node
import { spawn } from "node:child_process";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { Command } from "commander";
import {
  loadEnvFiles,
  loadConfig,
  saveConfig,
  openDatabase,
  MemoryStore,
  runHealth,
  indexProject,
  redactObject,
} from "@forgemind/core";
import { brand } from "./ui.js";
import { startChat } from "./chat.js";

// Carrega ./.env e ~/.forgemind/.env antes de tudo, para que Gemini/local-llama
// funcionem de QUALQUER diretorio sem erro de chave ausente.
loadEnvFiles();

const here = dirname(fileURLToPath(import.meta.url));
const serverEntry = resolve(here, "../../server/dist/index.js");

const program = new Command();
program
  .name("forgemind")
  .description("ForgeMind EAI — IA pessoal de desenvolvimento, local e offline.")
  .version("0.1.0");

// Sem subcomando => abre o chat estilo Claude Code.
program.action(async () => {
  await startChat();
});

program.command("chat").description("conversa no terminal (offline)").action(startChat);

program
  .command("start")
  .description("sobe o servidor local (site + API)")
  .option("-d, --detach", "roda em segundo plano")
  .action((opts) => {
    if (!existsSync(serverEntry)) {
      console.log(brand.err("Servidor nao compilado. Rode: npm run build"));
      process.exit(1);
    }
    const cfg = loadConfig();
    const url = `http://${cfg.host}:${cfg.port}`;
    console.log(brand.primary(`◆ subindo ForgeMind em ${brand.you(url)} ...`));
    const child = spawn(process.execPath, [serverEntry], {
      stdio: opts.detach ? "ignore" : "inherit",
      detached: !!opts.detach,
    });
    if (opts.detach) {
      child.unref();
      console.log(brand.ok(`✔ rodando em segundo plano. Site: ${url}`));
    }
  });

program
  .command("localhost")
  .alias("site")
  .description("mostra a URL do seu site local")
  .action(() => {
    const cfg = loadConfig();
    const url = `http://${cfg.host}:${cfg.port}`;
    console.log("\n" + brand.primary("◆ Seu site ForgeMind (local, so seu):"));
    console.log("  " + brand.you(url));
    console.log(brand.dim("  abra no navegador para conversar por la.\n"));
  });

program
  .command("doctor")
  .alias("diagnose")
  .description("diagnostico de saude do sistema")
  .action(async () => {
    const cfg = loadConfig();
    const db = openDatabase(cfg);
    const r = await runHealth(cfg, db);
    console.log(brand.primary("\n◆ ForgeMind doctor\n"));
    for (const c of r.checks) {
      console.log(`  ${c.ok ? brand.ok("✔") : brand.err("✘")} ${c.name.padEnd(16)} ${brand.dim(c.detail)}`);
    }
    console.log("\n  " + (r.ok ? brand.ok("tudo certo.") : brand.warn("ha itens a resolver.")) + "\n");
    process.exit(r.ok ? 0 : 1);
  });

program
  .command("index [path]")
  .description("indexa um projeto (padrao: pasta atual)")
  .action((path?: string) => {
    const cfg = loadConfig();
    const db = openDatabase(cfg);
    const root = resolve(path ?? process.cwd());
    console.log(brand.dim(`indexando ${root} ...`));
    const s = indexProject(db, root);
    console.log(brand.ok(`✔ ${s.files} arquivos, ${s.symbols} simbolos (${s.skipped} ignorados)`));
  });

program
  .command("memory [query]")
  .description("lista ou pesquisa a memoria")
  .action((query?: string) => {
    const cfg = loadConfig();
    const db = openDatabase(cfg);
    const mem = new MemoryStore(db);
    const items = query ? mem.searchMemory(query) : mem.listMemory(undefined, 20);
    for (const m of items) console.log(`${brand.accent("#" + m.id)} ${brand.dim(m.kind)} ${m.value.slice(0, 100)}`);
    if (items.length === 0) console.log(brand.dim("(memoria vazia)"));
  });

program
  .command("backup")
  .description("exporta memoria/historico para JSON (sem segredos)")
  .action(() => {
    const cfg = loadConfig();
    const db = openDatabase(cfg);
    const mem = new MemoryStore(db);
    const dir = join(cfg.home, "backups");
    mkdirSync(dir, { recursive: true });
    const file = join(dir, `backup-${Date.now()}.json`);
    writeFileSync(file, JSON.stringify(redactObject(mem.export()), null, 2));
    console.log(brand.ok(`✔ backup salvo em ${file}`));
  });

program
  .command("model:pull")
  .description("instrucoes para baixar o modelo local (Qwen2.5-Coder-3B)")
  .action(() => {
    const cfg = loadConfig();
    console.log(
      [
        brand.primary("\n◆ Baixar o cerebro local (uma vez, com internet; depois offline)\n"),
        "Recomendado (codigo/inline): " + brand.accent("Qwen2.5-Coder-3B Q4_K_M") + " (~2GB, com FIM p/ inline)",
        "",
        brand.dim("  # opcao 1: script pronto"),
        "  ./scripts/model-pull.sh",
        "",
        brand.dim("  # opcao 2: manual"),
        "  mkdir -p models && cd models",
        "  curl -L -o qwen2.5-coder-3b-instruct-q4_k_m.gguf \\",
        "    https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct-GGUF/resolve/main/qwen2.5-coder-3b-instruct-q4_k_m.gguf",
        "",
        "Depois, em " + brand.you(`http://${cfg.host}:${cfg.port}`) + " (/config) escolha o provider " + brand.accent("local-llama") + ".",
        brand.dim("Modo rapido (menos RAM): troque para o modelo 1.5B.\n"),
      ].join("\n"),
    );
  });

program
  .command("provider [name]")
  .description("mostra ou troca o cerebro: heuristic | local-llama | gemini")
  .action((name?: string) => {
    const cfg = loadConfig();
    if (!name) {
      console.log(`\n  provider atual: ${brand.accent(cfg.provider)}`);
      console.log(brand.dim("  troque com: forgemind provider gemini\n"));
      return;
    }
    const valid = ["heuristic", "local-llama", "gemini"];
    if (!valid.includes(name)) {
      console.log(brand.err(`  invalido: ${name}. Use: ${valid.join(" | ")}`));
      process.exit(1);
    }
    saveConfig({ provider: name as "heuristic" | "local-llama" | "gemini" });
    console.log(brand.ok(`✔ provider agora e ${name}.`));
    if (name === "gemini" && !process.env.GEMINI_API_KEY) {
      console.log(brand.warn("  falta a chave. Rode: forgemind gemini SUA_CHAVE"));
    }
  });

program
  .command("gemini <apikey> [model]")
  .description("ativa o Gemini em qualquer terminal (salva a chave no .env global)")
  .action((apikey: string, model?: string) => {
    const cfg = loadConfig();
    mkdirSync(cfg.home, { recursive: true });
    const envPath = join(cfg.home, ".env");
    const kv: Record<string, string> = {
      AI_PROVIDER: "gemini",
      GEMINI_API_KEY: apikey,
      GEMINI_MODEL: model ?? cfg.gemini.model ?? "gemini-1.5-flash",
    };
    writeEnv(envPath, kv);
    saveConfig({ provider: "gemini", gemini: { model: kv.GEMINI_MODEL } as any });
    console.log(brand.ok(`\n✔ Gemini ativado (modelo ${kv.GEMINI_MODEL}).`));
    console.log(brand.dim(`  chave salva em ${envPath} (fora do git, nunca no config.json).`));
    console.log(brand.dim("  funciona agora de qualquer diretorio: forgemind\n"));
  });

/** Atualiza (ou insere) pares chave=valor num arquivo .env preservando o resto. */
function writeEnv(path: string, kv: Record<string, string>): void {
  const existing = existsSync(path) ? readFileSync(path, "utf8").split("\n") : [];
  const seen = new Set<string>();
  const out = existing.map((line) => {
    const m = line.match(/^([A-Z0-9_]+)=/);
    if (m && kv[m[1]!] !== undefined) {
      seen.add(m[1]!);
      return `${m[1]}=${kv[m[1]!]}`;
    }
    return line;
  });
  for (const [k, v] of Object.entries(kv)) if (!seen.has(k)) out.push(`${k}=${v}`);
  writeFileSync(path, out.filter((l, i, a) => !(l === "" && a[i - 1] === "")).join("\n").replace(/\n*$/, "\n"));
}

program.parseAsync(process.argv);
