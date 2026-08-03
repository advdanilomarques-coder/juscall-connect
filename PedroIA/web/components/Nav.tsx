"use client";
import { useEffect, useState } from "react";
import { MARKETPLACE_URL } from "@/lib/links";

export default function Nav() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition ${
        scrolled ? "backdrop-blur-xl bg-ink/70 border-b border-white/5" : ""
      }`}
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <a href="#hero" className="flex items-center gap-2 font-display text-lg font-bold">
          <span className="grid h-8 w-8 place-items-center rounded-lg text-ink glow"
            style={{ background: "linear-gradient(135deg,#7c3aed,#22d3ee)" }}>
            {"</>"}
          </span>
          Pedro<span className="text-gradient">IA</span>
        </a>
        <div className="hidden items-center gap-8 text-sm text-frost/70 md:flex">
          <a href="#poder" className="hover:text-frost">Recursos</a>
          <a href="#como" className="hover:text-frost">Como funciona</a>
          <a href="#sobre" className="hover:text-frost">Sobre</a>
          <a href="#comunidade" className="hover:text-frost">Comunidade</a>
        </div>
        <a href={MARKETPLACE_URL} target="_blank" rel="noopener noreferrer" className="btn-primary text-sm">
          Download
        </a>
      </nav>
    </header>
  );
}
