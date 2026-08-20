#!/usr/bin/env node
import { spawn } from "node:child_process";
import { existsSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { Command } from "commander";
import {
  loadConfig,
  openDatabase,
  MemoryStore,
  runHealth,
  indexProject,
  redactObject,
} from "@forgemind/core";
import { brand } from "./ui.js";
import { startChat } from "./chat.js";

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
  .description("instrucoes para baixar o modelo local (Qwen2.5-3B)")
  .action(() => {
    const cfg = loadConfig();
    console.log(
      [
        brand.primary("\n◆ Baixar o cerebro local (uma vez, com internet; depois offline)\n"),
        "Recomendado p/ seu Mac (10GB): " + brand.accent("Qwen2.5-3B-Instruct Q4_K_M") + " (~2GB)",
        "",
        brand.dim("  # opcao 1: script pronto"),
        "  ./scripts/model-pull.sh",
        "",
        brand.dim("  # opcao 2: manual"),
        "  mkdir -p models && cd models",
        "  curl -L -o qwen2.5-3b-instruct-q4_k_m.gguf \\",
        "    https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf",
        "",
        "Depois, em " + brand.you(`http://${cfg.host}:${cfg.port}`) + " (/config) escolha o provider " + brand.accent("local-llama") + ".",
        brand.dim("Modo rapido (menos RAM): troque para o modelo 1.5B.\n"),
      ].join("\n"),
    );
  });

program.parseAsync(process.argv);
