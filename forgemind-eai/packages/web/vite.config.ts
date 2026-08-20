import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Base relativa: o site e servido pelo proprio backend local (nunca hospedado).
export default defineConfig({
  base: "./",
  plugins: [react()],
  server: {
    port: 4318,
    // Em dev, encaminha /api para o backend local do ForgeMind.
    proxy: {
      "/api": "http://127.0.0.1:4319",
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
