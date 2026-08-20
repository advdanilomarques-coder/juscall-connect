import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const root = dirname(fileURLToPath(import.meta.url));

// Config isolada: impede o vitest de subir e achar o vite.config.ts do repo pai.
export default {
  root,
  // Impede o vite de subir e carregar o postcss/tailwind do repo pai.
  css: { postcss: { plugins: [] } },
  test: {
    root,
    include: ["test/**/*.test.ts"],
    environment: "node",
  },
};
