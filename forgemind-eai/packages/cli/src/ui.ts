import pc from "picocolors";

/** Truecolor ANSI (picocolors nao tem hex). Respeita NO_COLOR / TTY. */
function rgb(r: number, g: number, b: number): (s: string) => string {
  const enabled = pc.isColorSupported;
  return (s: string) => (enabled ? `\x1b[38;2;${r};${g};${b}m${s}\x1b[39m` : s);
}

const ember = rgb(255, 122, 26); // #FF7A1A
const amber = rgb(255, 180, 84); // #FFB454

/** Paleta ForgeMind (forja/brasa): laranja/ambar sobre grafite. */
export const brand = {
  primary: (s: string) => ember(s),
  accent: (s: string) => amber(s),
  dim: (s: string) => pc.dim(s),
  ok: (s: string) => pc.green(s),
  warn: (s: string) => pc.yellow(s),
  err: (s: string) => pc.red(s),
  you: (s: string) => pc.cyan(s),
  ai: (s: string) => ember(s),
};

const ANSI = /\x1b\[[0-9;]*m/g; // eslint-disable-line no-control-regex
const visibleLen = (s: string): number => s.replace(ANSI, "").length;
const width = () => Math.min(process.stdout.columns ?? 80, 80);

/** Banner estilo Claude Code (caixa arredondada + dica). */
export function banner(provider: string, offline: boolean, site: string): string {
  const w = width();
  const line = "─".repeat(w - 2);
  const mode = offline ? brand.ok("● offline") : brand.warn("● online");
  const rows = [
    brand.primary("╭" + line + "╮"),
    boxRow(w, `${brand.primary("◆")} ${pc.bold("ForgeMind EAI")} ${brand.dim("— IA de desenvolvimento local")}`),
    boxRow(w, `${brand.dim("provider:")} ${brand.accent(provider)}   ${mode}`),
    boxRow(w, `${brand.dim("site:")} ${brand.you(site)}`),
    boxRow(w, brand.dim("digite ") + brand.accent("/help") + brand.dim(" para comandos, ") + brand.accent("/site") + brand.dim(" para o localhost")),
    brand.primary("╰" + line + "╯"),
  ];
  return rows.join("\n");
}

function boxRow(w: number, content: string): string {
  const pad = Math.max(0, w - 2 - 2 - visibleLen(content));
  return brand.primary("│") + " " + content + " ".repeat(pad) + " " + brand.primary("│");
}

export function youPrompt(): string {
  return brand.you("❯ ");
}

export function aiLabel(): string {
  return brand.ai("◆ forgemind ");
}

export function hr(): string {
  return brand.dim("─".repeat(width()));
}
