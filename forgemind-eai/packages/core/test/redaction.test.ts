import { describe, expect, it } from "vitest";
import { redactSecrets, isSensitiveFile } from "../src/redaction.js";

describe("redaction", () => {
  it("redige chaves do Google/Gemini", () => {
    const s = redactSecrets("GEMINI_API_KEY=AIzaSyA1234567890abcdefghijklmnopqrstuv");
    expect(s).not.toContain("AIzaSyA1234567890");
    expect(s).toContain("REDACTED");
  });

  it("redige tokens no formato key=value", () => {
    expect(redactSecrets("password=supersecret123")).toContain("REDACTED");
    expect(redactSecrets("api_key: abc123def456")).toContain("REDACTED");
  });

  it("redige JWT", () => {
    const jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abcDEF123456";
    expect(redactSecrets(jwt)).toContain("REDACTED_JWT");
  });

  it("nao altera texto comum", () => {
    expect(redactSecrets("ola mundo")).toBe("ola mundo");
  });

  it("detecta arquivos sensiveis", () => {
    expect(isSensitiveFile(".env")).toBe(true);
    expect(isSensitiveFile("config/id_rsa")).toBe(true);
    expect(isSensitiveFile("src/app.ts")).toBe(false);
  });
});
