import { existsSync } from "node:fs";
import { join } from "node:path";

/**
 * Terminal AI (PDF item 28-31): explica, sugere e corrige comandos, e oferece
 * Ghost Text de terminal — SEM executar nada automaticamente. Tudo offline e
 * deterministico; considera diretorio atual, arquivos, historico e SO.
 */

export interface TerminalContext {
  cwd: string;
  os: NodeJS.Platform;
  recent: string[]; // comandos recentes (mais novo por ultimo)
  files?: string[]; // nomes no cwd (opcional)
}

const DANGEROUS = [
  /\brm\s+-rf?\b/, /\bmkfs\b/, /\bdd\s+if=/, /:\(\)\s*\{/, /\bchmod\s+-R\s+777/,
  /\b>\s*\/dev\/sd/, /\bgit\s+push\s+--force\b/, /\bsudo\s+rm\b/, /\bshutdown\b/, /\breboot\b/,
];

/** true se o comando exige confirmacao explicita (PDF item 30). */
export function isDangerous(cmd: string): boolean {
  return DANGEROUS.some((re) => re.test(cmd));
}

/** Ghost Text de terminal: sugere a continuacao do que esta sendo digitado. */
export function terminalGhost(partial: string, ctx: TerminalContext): { text: string; confidence: number } {
  const p = partial.trimStart();
  if (p.length < 2) return { text: "", confidence: 0 };

  // 1) Match com historico recente (prefixo)
  const hist = [...ctx.recent].reverse().find((c) => c.startsWith(p) && c !== p);
  if (hist) return { text: hist.slice(p.length), confidence: 0.6 };

  // 2) Sugestoes por projeto detectado no cwd
  const proj = detectProject(ctx.cwd);
  const suggestions = COMMANDS[proj] ?? [];
  const match = suggestions.find((c) => c.startsWith(p) && c !== p);
  if (match) return { text: match.slice(p.length), confidence: 0.5 };

  // 3) Padroes genericos
  const generic = GENERIC.find((c) => c.startsWith(p) && c !== p);
  if (generic) return { text: generic.slice(p.length), confidence: 0.4 };

  return { text: "", confidence: 0 };
}

/** Explica um comando em linguagem simples (offline). */
export function explainCommand(cmd: string): string {
  const parts = cmd.trim().split(/\s+/);
  const base = parts[0] ?? "";
  const known = EXPLAIN[base];
  const danger = isDangerous(cmd) ? "\n\n⚠️  Comando potencialmente destrutivo — confirme antes de executar." : "";
  if (known) return known + danger;
  return `\`${base}\` — nao tenho uma explicacao offline especifica. Estrutura: comando + flags + argumentos.${danger}`;
}

function detectProject(cwd: string): string {
  if (existsSync(join(cwd, "package.json"))) return "node";
  if (existsSync(join(cwd, "pyproject.toml")) || existsSync(join(cwd, "requirements.txt"))) return "python";
  if (existsSync(join(cwd, "Cargo.toml"))) return "rust";
  if (existsSync(join(cwd, "go.mod"))) return "go";
  if (existsSync(join(cwd, "pom.xml")) || existsSync(join(cwd, "build.gradle"))) return "java";
  return "generic";
}

const COMMANDS: Record<string, string[]> = {
  node: ["npm install", "npm run build", "npm run dev", "npm test", "npm run lint", "node ."],
  python: ["python -m venv .venv", "source .venv/bin/activate", "pip install -r requirements.txt", "pytest"],
  rust: ["cargo build", "cargo run", "cargo test", "cargo clippy"],
  go: ["go build ./...", "go run .", "go test ./...", "go mod tidy"],
  java: ["mvn clean install", "mvn test", "./gradlew build"],
};

const GENERIC = ["git status", "git add .", "git commit -m ", "git push", "git pull", "ls -la", "cd ..", "grep -rn "];

const EXPLAIN: Record<string, string> = {
  git: "`git` — controle de versao. Ex.: status, add, commit, push, pull, log, diff, branch.",
  npm: "`npm` — gerenciador de pacotes Node. Ex.: install, run <script>, test, ci.",
  ls: "`ls` — lista arquivos. `-la` mostra ocultos e detalhes.",
  cd: "`cd` — muda de diretorio.",
  grep: "`grep` — busca padroes em texto. `-r` recursivo, `-n` numero da linha.",
  rm: "`rm` — remove arquivos. `-r` recursivo, `-f` forca. PERIGOSO.",
  curl: "`curl` — cliente HTTP de linha de comando.",
  docker: "`docker` — containers. Ex.: ps, build, run, compose up.",
};
