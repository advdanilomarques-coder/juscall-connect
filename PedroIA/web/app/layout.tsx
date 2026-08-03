import type { Metadata, Viewport } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const space = Space_Grotesk({ subsets: ["latin"], variable: "--font-space", display: "swap" });

const SITE_URL = "https://pedroia.dev";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: "PedroIA — Inteligência Artificial para Desenvolvedores",
  description:
    "PedroIA é um agente de inteligência artificial integrado ao VS Code capaz de criar códigos, corrigir erros e auxiliar desenvolvedores.",
  keywords: ["PedroIA", "IA", "VS Code", "autocomplete", "copilot", "programação", "assistente de código"],
  authors: [{ name: "PedroIA" }],
  openGraph: {
    title: "PedroIA — Seu engenheiro de IA no VS Code",
    description:
      "Uma IA profissional integrada ao VS Code capaz de criar, corrigir e evoluir seus projetos.",
    url: SITE_URL,
    siteName: "PedroIA",
    locale: "pt_BR",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "PedroIA — Inteligência Artificial para Desenvolvedores",
    description:
      "Um agente de IA integrado ao VS Code capaz de criar, corrigir e evoluir seus projetos.",
  },
  robots: { index: true, follow: true },
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
    ],
  },
};

export const viewport: Viewport = {
  themeColor: "#05050a",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${inter.variable} ${space.variable}`}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
