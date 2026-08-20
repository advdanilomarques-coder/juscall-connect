import { describe, expect, it } from "vitest";
import { extractImports, extractSymbols, languageOf, resolveModule } from "../src/indexer.js";

describe("indexer", () => {
  it("detecta linguagem por extensao", () => {
    expect(languageOf("a/b/App.tsx")).toBe("typescriptreact");
    expect(languageOf("x.py")).toBe("python");
    expect(languageOf("main.go")).toBe("go");
  });

  it("extrai imports TS com nomes", () => {
    const src = `import { foo, bar as baz } from "./util";\nimport React from "react";\nimport "./styles.css";`;
    const imps = extractImports(src, "typescript");
    const util = imps.find((i) => i.module === "./util");
    expect(util?.names).toContain("foo");
    expect(util?.names).toContain("bar");
    expect(imps.map((i) => i.module)).toContain("react");
    expect(imps.map((i) => i.module)).toContain("./styles.css");
  });

  it("extrai imports Python", () => {
    const src = `from app.core import Engine, Store\nimport os`;
    const imps = extractImports(src, "python");
    expect(imps.find((i) => i.module === "app.core")?.names).toContain("Engine");
    expect(imps.map((i) => i.module)).toContain("os");
  });

  it("marca exports em TS", () => {
    const syms = extractSymbols(`export function pub() {}\nfunction priv() {}`, "typescript");
    expect(syms.find((s) => s.name === "pub")?.exported).toBe(true);
    expect(syms.find((s) => s.name === "priv")?.exported).toBe(false);
  });

  it("resolveModule retorna null para dependencia externa", () => {
    expect(resolveModule("src/a.ts", "react", "/tmp/proj")).toBeNull();
  });
});
