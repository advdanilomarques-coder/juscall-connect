/**
 * Redaction de segredos.
 *
 * Regra do ForgeMind (PDF item 11 e 47): nunca enviar/registrar .env, API keys,
 * senhas, tokens, certificados ou dados sensiveis desnecessarios. Esta funcao e
 * o ultimo guarda antes de qualquer log, backup ou chamada a provider externo.
 */

const PATTERNS: Array<{ re: RegExp; replace: string }> = [
  // key=value / key: value com nomes sensiveis
  {
    re: /\b([A-Za-z0-9_]*(?:api[_-]?key|secret|token|password|passwd|pwd|auth|bearer|private[_-]?key|access[_-]?key)[A-Za-z0-9_]*)\s*[:=]\s*["']?([^\s"',;]+)/gi,
    replace: "$1=***REDACTED***",
  },
  // Google / Gemini API keys
  { re: /AIza[0-9A-Za-z\-_]{20,}/g, replace: "***REDACTED_GOOGLE_KEY***" },
  // OpenAI-style keys
  { re: /sk-[A-Za-z0-9]{20,}/g, replace: "***REDACTED_KEY***" },
  // GitHub tokens
  { re: /gh[pousr]_[A-Za-z0-9]{20,}/g, replace: "***REDACTED_GH_TOKEN***" },
  // JWT
  { re: /eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}/g, replace: "***REDACTED_JWT***" },
  // Authorization headers
  { re: /(Authorization:\s*Bearer\s+)[^\s]+/gi, replace: "$1***REDACTED***" },
  // PEM blocks
  {
    re: /-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----/g,
    replace: "***REDACTED_PRIVATE_KEY***",
  },
];

const SENSITIVE_FILE = /(^|\/)\.env(\.[a-z]+)?$|\.pem$|\.key$|id_rsa|id_ed25519|\.p12$|\.pfx$/i;

export function redactSecrets(input: string): string {
  let out = input;
  for (const { re, replace } of PATTERNS) out = out.replace(re, replace);
  return out;
}

/** True se o caminho aponta para um arquivo sensivel que nunca deve ir a IA/backup. */
export function isSensitiveFile(path: string): boolean {
  return SENSITIVE_FILE.test(path);
}

/** Redige recursivamente um objeto (para respostas de API/config). */
export function redactObject<T>(obj: T): T {
  const json = JSON.stringify(obj);
  return JSON.parse(redactSecrets(json)) as T;
}
