"use client";
import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import ParticlesBackground from "./ParticlesBackground";
import { MARKETPLACE_URL } from "@/lib/links";

const CODE_LINES = [
  "const pedro = new PedroIA();",
  "await pedro.analisar(projeto);",
  "await pedro.corrigir(bugs);",
  "await pedro.evoluir(codigo); // ✨",
];

export default function Hero() {
  const root = useRef<HTMLElement>(null);
  const [typed, setTyped] = useState("");

  // animação de entrada
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from("[data-hero]", {
        y: 30,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
        stagger: 0.15,
        delay: 0.2,
      });
    }, root);
    return () => ctx.revert();
  }, []);

  // efeito de "digitação" do código
  useEffect(() => {
    const full = CODE_LINES.join("\n");
    let i = 0;
    const id = setInterval(() => {
      setTyped(full.slice(0, i++));
      if (i > full.length) clearInterval(id);
    }, 45);
    return () => clearInterval(id);
  }, []);

  return (
    <section ref={root} id="hero" className="relative flex min-h-screen items-center overflow-hidden grid-bg">
      <ParticlesBackground />
      <div className="absolute inset-0 -z-10 bg-gradient-to-b from-transparent via-ink/40 to-ink" />

      <div className="mx-auto grid w-full max-w-7xl grid-cols-1 items-center gap-12 px-6 pt-28 lg:grid-cols-2">
        <div>
          <span data-hero className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs text-frost/70">
            <span className="h-2 w-2 rounded-full bg-neon animate-pulse" /> IA integrada ao VS Code
          </span>
          <h1 data-hero className="mt-6 font-display text-5xl font-bold leading-[1.05] sm:text-6xl">
            Seu novo <span className="text-gradient">engenheiro de software</span> com inteligência artificial.
          </h1>
          <p data-hero className="mt-6 max-w-xl text-lg text-frost/70">
            Uma IA profissional integrada ao VS Code capaz de <b>criar</b>, <b>corrigir</b> e <b>evoluir</b> seus projetos.
          </p>
          <div data-hero className="mt-9 flex flex-wrap gap-4">
            <a href={MARKETPLACE_URL} target="_blank" rel="noopener noreferrer" className="btn-primary">
              ⬇ Download PedroIA Extension
            </a>
            <a href="#engenheiro" className="btn-ghost">Conheça o PedroIA</a>
          </div>
        </div>

        {/* Janela de código flutuante */}
        <div data-hero className="animate-floaty">
          <div className="overflow-hidden rounded-2xl border border-white/10 bg-panel/80 shadow-2xl glow backdrop-blur">
            <div className="flex items-center gap-2 border-b border-white/5 px-4 py-3">
              <span className="h-3 w-3 rounded-full bg-red-400/80" />
              <span className="h-3 w-3 rounded-full bg-yellow-400/80" />
              <span className="h-3 w-3 rounded-full bg-green-400/80" />
              <span className="ml-3 text-xs text-frost/40">pedroia.ts</span>
            </div>
            <pre className="min-h-[180px] whitespace-pre-wrap p-5 font-mono text-sm leading-relaxed text-neon">
              {typed}
              <span className="animate-blink">▍</span>
            </pre>
          </div>
        </div>
      </div>

      <a href="#engenheiro" className="absolute bottom-8 left-1/2 -translate-x-1/2 text-frost/40" aria-label="Rolar">
        <span className="block h-10 w-6 rounded-full border border-frost/30">
          <span className="mx-auto mt-2 block h-2 w-1 animate-bounce rounded-full bg-frost/60" />
        </span>
      </a>
    </section>
  );
}
