import type { DB } from "./db.js";
import { projectId } from "./indexer.js";

interface SymbolRow {
  name: string;
  kind: string;
  line: number;
  signature: string | null;
  path: string;
  language: string;
  exported: number;
}

/**
 * Context Retriever (PDF item 13/16/18): monta um contexto RELEVANTE e pequeno
 * a partir do indice — nunca o projeto inteiro. Ranqueia por match de termos,
 * dando peso a simbolos exportados (API publica).
 */
export function retrieveContext(
  db: DB,
  root: string,
  query: string,
  opts: { maxSymbols?: number; maxChars?: number } = {},
): string {
  const project = projectId(root);
  const maxSymbols = opts.maxSymbols ?? 20;
  const maxChars = opts.maxChars ?? 2000;
  const terms = tokenize(query);
  if (terms.length === 0) return "";

  const rows = allSymbols(db, project);
  const scored = rows
    .map((r) => ({ r, s: score(r.name, r.signature ?? "", terms) + (r.exported ? 1 : 0) }))
    .filter((x) => x.s > 0)
    .sort((a, b) => b.s - a.s)
    .slice(0, maxSymbols);

  if (scored.length === 0) return "";
  return clamp("Simbolos relevantes do projeto:\n" + scored.map(({ r }) => fmt(r)).join("\n"), maxChars);
}

/**
 * Contexto CRUZADO para um arquivo (inline e Q&A): junta os simbolos do proprio
 * arquivo + os simbolos EXPORTADOS dos modulos locais que ele importa. Assim o
 * ForgeMind entende as relacoes entre arquivos sem enviar a base inteira.
 */
export function retrieveFileContext(
  db: DB,
  root: string,
  filePath: string,
  query: string,
  opts: { maxSymbols?: number; maxChars?: number } = {},
): string {
  const project = projectId(root);
  const maxSymbols = opts.maxSymbols ?? 24;
  const maxChars = opts.maxChars ?? 2400;

  const file = db
    .prepare("SELECT id, path FROM project_files WHERE project = ? AND path = ?")
    .get(project, filePath) as { id: number; path: string } | undefined;

  const blocks: string[] = [];
  const terms = tokenize(query);

  if (file) {
    // 1) simbolos do proprio arquivo
    const own = db
      .prepare("SELECT s.*, f.path, f.language FROM project_symbols s JOIN project_files f ON f.id = s.file_id WHERE s.file_id = ? LIMIT 40")
      .all(file.id) as SymbolRow[];
    if (own.length) blocks.push(`Arquivo atual (${file.path}):\n` + own.slice(0, 14).map(fmt).join("\n"));

    // 2) imports locais -> simbolos exportados desses arquivos
    const imps = db
      .prepare("SELECT resolved_path, names FROM project_imports WHERE file_id = ? AND resolved_path IS NOT NULL")
      .all(file.id) as Array<{ resolved_path: string; names: string | null }>;
    for (const imp of imps.slice(0, 8)) {
      const syms = db
        .prepare(
          `SELECT s.*, f.path, f.language FROM project_symbols s JOIN project_files f ON f.id = s.file_id
           WHERE f.project = ? AND f.path = ? AND s.exported = 1 LIMIT 12`,
        )
        .all(project, imp.resolved_path) as SymbolRow[];
      if (syms.length) blocks.push(`Importado de ${imp.resolved_path}:\n` + syms.map(fmt).join("\n"));
    }
  }

  // 3) complementa com melhores matches globais da consulta
  if (terms.length) {
    const rows = allSymbols(db, project);
    const extra = rows
      .map((r) => ({ r, s: score(r.name, r.signature ?? "", terms) + (r.exported ? 1 : 0) }))
      .filter((x) => x.s > 0)
      .sort((a, b) => b.s - a.s)
      .slice(0, maxSymbols)
      .map(({ r }) => fmt(r));
    if (extra.length) blocks.push("Outros relevantes:\n" + extra.join("\n"));
  }

  return clamp(blocks.join("\n\n"), maxChars);
}

function allSymbols(db: DB, project: string): SymbolRow[] {
  return db
    .prepare(
      `SELECT s.name, s.kind, s.line, s.signature, s.exported, f.path, f.language
       FROM project_symbols s JOIN project_files f ON f.id = s.file_id WHERE f.project = ?`,
    )
    .all(project) as SymbolRow[];
}

function fmt(r: SymbolRow): string {
  return `- ${r.path}:${r.line} (${r.kind}${r.exported ? ",export" : ""}) ${r.name}${r.signature ? ` — ${r.signature}` : ""}`;
}

function clamp(text: string, maxChars: number): string {
  return text.length > maxChars ? text.slice(0, maxChars) + "\n…(truncado)" : text;
}

function tokenize(s: string): string[] {
  return [...new Set((s.match(/[A-Za-z_$][A-Za-z0-9_$]{2,}/g) ?? []).map((t) => t.toLowerCase()))].slice(0, 12);
}

function score(name: string, sig: string, terms: string[]): number {
  const n = name.toLowerCase();
  const s = sig.toLowerCase();
  let total = 0;
  for (const t of terms) {
    if (n === t) total += 5;
    else if (n.startsWith(t)) total += 3;
    else if (n.includes(t)) total += 2;
    else if (s.includes(t)) total += 1;
  }
  return total;
}
