// Backend + external links. Override VITE_API_URL at build time on Vercel/Netlify.
export const API_URL = (import.meta.env.VITE_API_URL as string) || "https://pedroia-backend.onrender.com";

// Marketplace link (fill in after publishing). Falls back to the GitHub repo.
export const VSCODE_MARKETPLACE_URL =
  (import.meta.env.VITE_MARKETPLACE_URL as string) ||
  "https://github.com/advdanilomarques-coder/juscall-connect/tree/main/PedroIA";

export const GITHUB_URL = "https://github.com/advdanilomarques-coder/juscall-connect";
