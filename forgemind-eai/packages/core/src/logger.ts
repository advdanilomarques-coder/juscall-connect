import { appendFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { redactSecrets } from "./redaction.js";

export type LogLevel = "debug" | "info" | "warn" | "error";

const LEVEL_ORDER: Record<LogLevel, number> = { debug: 0, info: 1, warn: 2, error: 3 };

let minLevel: LogLevel = (process.env.FORGEMIND_LOG_LEVEL as LogLevel) || "info";
let logFile: string | null = null;

export function configureLogger(opts: { level?: LogLevel; file?: string }): void {
  if (opts.level) minLevel = opts.level;
  if (opts.file) {
    logFile = opts.file;
    try {
      mkdirSync(dirname(opts.file), { recursive: true });
    } catch {
      /* ignore */
    }
  }
}

function write(level: LogLevel, msg: string, meta?: unknown): void {
  if (LEVEL_ORDER[level] < LEVEL_ORDER[minLevel]) return;
  const time = new Date().toISOString();
  // Secrets are ALWAYS redacted before they reach a log sink.
  const safeMsg = redactSecrets(msg);
  const safeMeta = meta === undefined ? "" : " " + redactSecrets(JSON.stringify(meta));
  const line = `[${time}] ${level.toUpperCase()} ${safeMsg}${safeMeta}`;
  const stream = level === "error" || level === "warn" ? process.stderr : process.stdout;
  stream.write(line + "\n");
  if (logFile) {
    try {
      appendFileSync(logFile, line + "\n");
    } catch {
      /* never crash on logging */
    }
  }
}

export const logger = {
  debug: (m: string, meta?: unknown) => write("debug", m, meta),
  info: (m: string, meta?: unknown) => write("info", m, meta),
  warn: (m: string, meta?: unknown) => write("warn", m, meta),
  error: (m: string, meta?: unknown) => write("error", m, meta),
  fileIn: (home: string) => join(home, "logs", "forgemind.log"),
};
