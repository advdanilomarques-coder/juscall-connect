import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { z } from "zod";

export const ProviderName = z.enum(["heuristic", "local-llama", "gemini", "hybrid"]);
export type ProviderName = z.infer<typeof ProviderName>;

export const InlineLevel = z.enum(["OFF", "LOW", "BALANCED", "HIGH"]);
export type InlineLevel = z.infer<typeof InlineLevel>;

export const ConfigSchema = z.object({
  provider: ProviderName.default("heuristic"),
  host: z.string().default("127.0.0.1"),
  port: z.number().int().min(1).max(65535).default(4319),
  home: z.string(),
  theme: z.enum(["light", "dark", "system"]).default("system"),
  inline: z
    .object({
      level: InlineLevel.default("BALANCED"),
      debounceMs: z.number().int().min(0).max(5000).default(350),
      minConfidence: z.number().min(0).max(1).default(0.35),
    })
    .default({}),
  localLlama: z
    .object({
      modelPath: z.string().default(""),
      contextSize: z.number().int().default(4096),
      threads: z.number().int().default(4),
    })
    .default({}),
  gemini: z
    .object({
      // A key NUNCA e persistida no config.json; vem so do ambiente.
      model: z.string().default("gemini-flash-latest"),
    })
    .default({}),
});

export type ForgeConfig = z.infer<typeof ConfigSchema>;

/** Campos que a UI pode editar. Secrets (chaves) ficam de fora de proposito. */
export type EditableConfig = Pick<ForgeConfig, "provider" | "theme" | "inline" | "localLlama"> & {
  gemini: { model: string };
  port: number;
  host: string;
};

function resolveHome(): string {
  const fromEnv = process.env.FORGEMIND_HOME?.trim();
  return fromEnv && fromEnv.length > 0 ? fromEnv : join(homedir(), ".forgemind");
}

function configPath(home: string): string {
  return join(home, "config.json");
}

/** Carrega config: defaults -> config.json -> variaveis de ambiente (env vence). */
export function loadConfig(): ForgeConfig {
  const home = resolveHome();
  mkdirSync(home, { recursive: true });

  let fromFile: Record<string, unknown> = {};
  const cp = configPath(home);
  if (existsSync(cp)) {
    try {
      fromFile = JSON.parse(readFileSync(cp, "utf8"));
    } catch {
      fromFile = {};
    }
  }

  const merged = ConfigSchema.parse({
    ...fromFile,
    home,
    provider: process.env.AI_PROVIDER ?? (fromFile as any).provider,
    host: process.env.FORGEMIND_HOST ?? (fromFile as any).host,
    port: process.env.FORGEMIND_PORT ? Number(process.env.FORGEMIND_PORT) : (fromFile as any).port,
    inline: {
      ...(fromFile as any).inline,
      level: process.env.INLINE_LEVEL ?? (fromFile as any).inline?.level,
      debounceMs: process.env.INLINE_DEBOUNCE_MS
        ? Number(process.env.INLINE_DEBOUNCE_MS)
        : (fromFile as any).inline?.debounceMs,
      minConfidence: process.env.INLINE_MIN_CONFIDENCE
        ? Number(process.env.INLINE_MIN_CONFIDENCE)
        : (fromFile as any).inline?.minConfidence,
    },
    localLlama: {
      ...(fromFile as any).localLlama,
      modelPath: process.env.LOCAL_MODEL_PATH ?? (fromFile as any).localLlama?.modelPath,
      contextSize: process.env.LOCAL_MODEL_CONTEXT
        ? Number(process.env.LOCAL_MODEL_CONTEXT)
        : (fromFile as any).localLlama?.contextSize,
      threads: process.env.LOCAL_MODEL_THREADS
        ? Number(process.env.LOCAL_MODEL_THREADS)
        : (fromFile as any).localLlama?.threads,
    },
    gemini: {
      ...(fromFile as any).gemini,
      model: process.env.GEMINI_MODEL ?? (fromFile as any).gemini?.model,
    },
  });

  return merged;
}

/** Persiste apenas campos nao-secretos em ~/.forgemind/config.json. */
export function saveConfig(patch: Partial<EditableConfig>): ForgeConfig {
  const current = loadConfig();
  const next: ForgeConfig = ConfigSchema.parse({
    ...current,
    ...patch,
    home: current.home,
    inline: { ...current.inline, ...(patch.inline ?? {}) },
    localLlama: { ...current.localLlama, ...(patch.localLlama ?? {}) },
    gemini: { ...current.gemini, ...(patch.gemini ?? {}) },
  });

  // Nunca gravar secrets. gemini.model e nao-secreto; a KEY nunca entra aqui.
  const { home, ...persistable } = next;
  mkdirSync(home, { recursive: true });
  writeFileSync(configPath(home), JSON.stringify(persistable, null, 2), "utf8");
  return next;
}

/** Le a Gemini API key SOMENTE do ambiente (nunca do disco de config). */
export function geminiApiKey(): string {
  return process.env.GEMINI_API_KEY?.trim() ?? "";
}

export function dataDir(cfg: ForgeConfig): string {
  const d = join(cfg.home, "data");
  mkdirSync(d, { recursive: true });
  return d;
}
