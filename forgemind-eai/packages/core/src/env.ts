import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

/**
 * Carregador de .env minimo (sem dependencia). Precedencia:
 *   process.env  >  ./.env (projeto)  >  ~/.forgemind/.env (global)
 *
 * Nunca sobrescreve o que ja esta no ambiente. Isso permite ativar o Gemini
 * (ou local-llama) de QUALQUER diretorio: basta a chave estar no .env global.
 */
export function loadEnvFiles(): void {
  const home = process.env.FORGEMIND_HOME?.trim() || join(homedir(), ".forgemind");
  // Carrega o do projeto primeiro (tem prioridade sobre o global);
  // como nunca sobrescreve, o que for setado antes vence.
  applyEnvFile(join(process.cwd(), ".env"));
  applyEnvFile(join(home, ".env"));
}

function applyEnvFile(path: string): void {
  if (!existsSync(path)) return;
  let text: string;
  try {
    text = readFileSync(path, "utf8");
  } catch {
    return;
  }
  for (const raw of text.split("\n")) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq <= 0) continue;
    const key = line.slice(0, eq).trim();
    if (key in process.env) continue; // nunca sobrescreve
    let val = line.slice(eq + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    process.env[key] = val;
  }
}
