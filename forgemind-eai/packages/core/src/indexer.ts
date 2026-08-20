import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { extname, join, relative } from "node:path";
import type { DB } from "./db.js";
import { isSensitiveFile } from "./redaction.js";

const IGNORE_DIRS = new Set([
  "node_modules", ".git", "dist", "build", ".next", ".turbo", "coverage",
  "__pycache__", ".venv", "venv", ".idea", ".vscode", "target", "vendor",
  ".cache", "models",
]);

const LANG_BY_EXT: Record<string, string> = {
  ".ts": "typescript", ".tsx": "typescriptreact", ".js": "javascript", ".jsx": "javascriptreact",
  ".py": "python", ".java": "java", ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php",
  ".c": "c", ".h": "c", ".cpp": "cpp", ".cc": "cpp", ".hpp": "cpp", ".cs": "csharp",
  ".kt": "kotlin", ".swift": "swift", ".dart": "dart", ".lua": "lua", ".r": "r",
  ".sql": "sql", ".sh": "bash", ".ps1": "powershell", ".vue": "vue", ".svelte": "svelte",
  ".html": "html", ".css": "css", ".scss": "scss", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
  ".md": "markdown", ".graphql": "graphql",
};

export function languageOf(path: string): string {
  return LANG_BY_EXT[extname(path).toLowerCase()] ?? "plaintext";
}

export interface IndexStats {
  project: string;
  files: number;
  symbols: number;
  skipped: number;
}

/**
 * Indexa incrementalmente um projeto (PDF item 16/17): so re-processa arquivos
 * cujo hash mudou. NUNCA le arquivos sensiveis (.env/.pem/keys). Agnostico a
 * linguagem via deteccao por extensao + extracao leve de simbolos por regex.
 *
 * Isso NAO envia o projeto a IA — apenas constroi um indice local para depois
 * recuperar so o contexto relevante.
 */
export function indexProject(db: DB, root: string, maxBytes = 400_000): IndexStats {
  const project = projectId(root);
  const stats: IndexStats = { project, files: 0, symbols: 0, skipped: 0 };

  const upsertFile = db.prepare(
    `INSERT INTO project_files (project, path, language, hash, size)
     VALUES (@project, @path, @language, @hash, @size)
     ON CONFLICT(project, path) DO UPDATE SET language=@language, hash=@hash, size=@size, indexed_at=datetime('now')`,
  );
  const getFile = db.prepare("SELECT id, hash FROM project_files WHERE project = ? AND path = ?");
  const clearSymbols = db.prepare("DELETE FROM project_symbols WHERE file_id = ?");
  const insSymbol = db.prepare(
    "INSERT INTO project_symbols (file_id, name, kind, line, signature) VALUES (?, ?, ?, ?, ?)",
  );

  const tx = db.transaction(() => {
    for (const abs of walk(root)) {
      const rel = relative(root, abs);
      if (isSensitiveFile(rel)) {
        stats.skipped++;
        continue;
      }
      const lang = languageOf(abs);
      if (lang === "plaintext" && !rel.endsWith(".txt")) {
        stats.skipped++;
        continue;
      }
      let content: string;
      let size: number;
      try {
        size = statSync(abs).size;
        if (size > maxBytes) {
          stats.skipped++;
          continue;
        }
        content = readFileSync(abs, "utf8");
      } catch {
        stats.skipped++;
        continue;
      }
      const hash = createHash("sha1").update(content).digest("hex");
      const existing = getFile.get(project, rel) as { id: number; hash: string } | undefined;
      if (existing && existing.hash === hash) {
        stats.files++;
        continue; // incremental: inalterado
      }
      upsertFile.run({ project, path: rel, language: lang, hash, size });
      const row = getFile.get(project, rel) as { id: number };
      clearSymbols.run(row.id);
      for (const sym of extractSymbols(content, lang)) {
        insSymbol.run(row.id, sym.name, sym.kind, sym.line, sym.signature ?? null);
        stats.symbols++;
      }
      stats.files++;
    }
  });
  tx();
  return stats;
}

export function projectId(root: string): string {
  return createHash("sha1").update(root).digest("hex").slice(0, 12);
}

function* walk(dir: string): Generator<string> {
  let entries: string[];
  try {
    entries = readdirSync(dir);
  } catch {
    return;
  }
  for (const name of entries) {
    if (name.startsWith(".") && name !== ".env.example") {
      if (IGNORE_DIRS.has(name)) continue;
    }
    const full = join(dir, name);
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isDirectory()) {
      if (IGNORE_DIRS.has(name)) continue;
      yield* walk(full);
    } else if (st.isFile()) {
      yield full;
    }
  }
}

interface Symbol {
  name: string;
  kind: string;
  line: number;
  signature?: string;
}

/** Extracao leve de simbolos por regex — agnostica, sem AST pesado. */
export function extractSymbols(content: string, lang: string): Symbol[] {
  const out: Symbol[] = [];
  const lines = content.split("\n");
  const rules = SYMBOL_RULES[lang] ?? SYMBOL_RULES.generic!;
  lines.forEach((line, i) => {
    for (const { re, kind } of rules) {
      const m = re.exec(line);
      if (m && m[1]) {
        out.push({ name: m[1], kind, line: i + 1, signature: line.trim().slice(0, 200) });
      }
    }
  });
  return out;
}

type Rule = { re: RegExp; kind: string };
const tsRules: Rule[] = [
  { re: /(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)/, kind: "function" },
  { re: /(?:export\s+)?class\s+([A-Za-z0-9_$]+)/, kind: "class" },
  { re: /(?:export\s+)?interface\s+([A-Za-z0-9_$]+)/, kind: "interface" },
  { re: /(?:export\s+)?type\s+([A-Za-z0-9_$]+)\s*=/, kind: "type" },
  { re: /(?:export\s+)?const\s+([A-Za-z0-9_$]+)\s*=/, kind: "const" },
];
const SYMBOL_RULES: Record<string, Rule[]> = {
  typescript: tsRules,
  typescriptreact: tsRules,
  javascript: tsRules,
  javascriptreact: tsRules,
  python: [
    { re: /^\s*def\s+([A-Za-z0-9_]+)/, kind: "function" },
    { re: /^\s*class\s+([A-Za-z0-9_]+)/, kind: "class" },
  ],
  go: [
    { re: /func\s+([A-Za-z0-9_]+)/, kind: "function" },
    { re: /type\s+([A-Za-z0-9_]+)\s+struct/, kind: "class" },
  ],
  rust: [
    { re: /fn\s+([A-Za-z0-9_]+)/, kind: "function" },
    { re: /struct\s+([A-Za-z0-9_]+)/, kind: "class" },
  ],
  java: [
    { re: /(?:public|private|protected)?\s*(?:static\s+)?[A-Za-z0-9_<>]+\s+([A-Za-z0-9_]+)\s*\(/, kind: "function" },
    { re: /class\s+([A-Za-z0-9_]+)/, kind: "class" },
  ],
  generic: [{ re: /(?:function|def|func|fn)\s+([A-Za-z0-9_]+)/, kind: "function" }],
};
