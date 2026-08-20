import { statfsSync } from "node:fs";
import { arch, freemem, platform, totalmem } from "node:os";
import type { ForgeConfig } from "./config.js";
import { createProvider } from "./providers/index.js";
import type { DB } from "./db.js";

export interface HealthCheck {
  name: string;
  ok: boolean;
  detail: string;
}

export interface HealthReport {
  ok: boolean;
  checks: HealthCheck[];
  timestamp: string;
}

/**
 * Health Monitor (PDF item 37): estado de node, arquitetura, SQLite, provider,
 * disco e memoria. Tudo local. Base para a Auto-Maintenance.
 */
export async function runHealth(cfg: ForgeConfig, db: DB | null): Promise<HealthReport> {
  const checks: HealthCheck[] = [];

  // Node
  const major = Number(process.versions.node.split(".")[0]);
  checks.push({
    name: "node",
    ok: major >= 20,
    detail: `Node ${process.versions.node} (alvo: 20.x+). Arch: ${arch()} / ${platform()}`,
  });

  // Arquitetura (PDF item 5 — macOS Intel x86_64)
  checks.push({
    name: "arch",
    ok: true,
    detail: arch() === "x64" ? "x86_64 (Intel) — alvo prioritario." : `${arch()} — suportado.`,
  });

  // SQLite
  if (db) {
    try {
      const v = db.prepare("SELECT sqlite_version() AS v").get() as { v: string };
      const conv = db.prepare("SELECT COUNT(*) AS n FROM conversations").get() as { n: number };
      checks.push({ name: "sqlite", ok: true, detail: `SQLite ${v.v}, ${conv.n} conversas.` });
    } catch (e) {
      checks.push({ name: "sqlite", ok: false, detail: `Erro no banco: ${(e as Error).message}` });
    }
  } else {
    checks.push({ name: "sqlite", ok: false, detail: "Banco nao inicializado." });
  }

  // Provider
  try {
    const p = createProvider(cfg);
    const h = await p.health();
    checks.push({ name: `provider:${p.name}`, ok: h.ok, detail: `${h.detail}${p.offline ? " [offline]" : " [online]"}` });
  } catch (e) {
    checks.push({ name: "provider", ok: false, detail: (e as Error).message });
  }

  // Memoria RAM
  const freeGb = (freemem() / 1e9).toFixed(1);
  const totalGb = (totalmem() / 1e9).toFixed(1);
  checks.push({ name: "memory", ok: freemem() > 200e6, detail: `RAM livre ${freeGb}GB / ${totalGb}GB` });

  // Disco
  try {
    const s = statfsSync(cfg.home);
    const freeGb2 = ((s.bavail * s.bsize) / 1e9).toFixed(1);
    checks.push({ name: "disk", ok: s.bavail * s.bsize > 100e6, detail: `Disco livre ${freeGb2}GB em ${cfg.home}` });
  } catch {
    checks.push({ name: "disk", ok: true, detail: "Disco: indisponivel (ignorado)." });
  }

  return { ok: checks.every((c) => c.ok), checks, timestamp: new Date().toISOString() };
}
