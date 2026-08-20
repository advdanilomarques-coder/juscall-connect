import { describe, expect, it } from "vitest";
import { heuristicCompletion } from "../src/providers/heuristic.js";
import { isDangerous, terminalGhost } from "../src/terminal.js";

describe("heuristicCompletion", () => {
  it("fecha parentese aberto", () => {
    const r = heuristicCompletion({ prefix: "foo(", suffix: "", language: "typescript" });
    expect(r.text).toBe(")");
    expect(r.confidence).toBeGreaterThan(0);
  });

  it("sugere corpo apos dois-pontos em python", () => {
    const r = heuristicCompletion({ prefix: "def foo():", suffix: "", language: "python" });
    expect(r.multiline).toBe(true);
    expect(r.text).toContain("\n");
  });

  it("nao sugere nada sem contexto util", () => {
    const r = heuristicCompletion({ prefix: "x", suffix: "", language: "plaintext" });
    expect(r.confidence).toBe(0);
  });
});

describe("terminal", () => {
  it("marca comandos perigosos", () => {
    expect(isDangerous("rm -rf /")).toBe(true);
    expect(isDangerous("git push --force")).toBe(true);
    expect(isDangerous("ls -la")).toBe(false);
  });

  it("completa a partir do historico", () => {
    const g = terminalGhost("git st", {
      cwd: "/tmp",
      os: "darwin",
      recent: ["git status", "npm test"],
    });
    expect(g.text).toBe("atus");
  });
});
