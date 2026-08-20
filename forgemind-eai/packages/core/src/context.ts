import type { DB } from "./db.js";
import { projectId } from "./indexer.js";

/**
 * Context Retriever (PDF item 13/16/18): monta um contexto RELEVANTE e pequeno
 * a partir do indice — nunca o projeto inteiro. Ranqueia simbolos por match de
 * termos da consulta/cursor e retorna um resumo textual limitado.
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

  const rows = db
    .prepare(
      `SELECT s.name, s.kind, s.line, s.signature, f.path, f.language
       FROM project_symbols s JOIN project_files f ON f.id = s.file_id
       WHERE f.project = ?`,
    )
    .all(project) as Array<{
    name: string;
    kind: string;
    line: number;
    signature: string | null;
    path: string;
    language: string;
  }>;

  const scored = rows
    .map((r) => ({ r, score: score(r.name, r.signature ?? "", terms) }))
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxSymbols);

  if (scored.length === 0) return "";

  const lines = scored.map(
    ({ r }) => `- ${r.path}:${r.line} (${r.kind}) ${r.name}${r.signature ? ` — ${r.signature}` : ""}`,
  );
  let text = "Simbolos relevantes do projeto:\n" + lines.join("\n");
  if (text.length > maxChars) text = text.slice(0, maxChars) + "\n…(truncado)";
  return text;
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
