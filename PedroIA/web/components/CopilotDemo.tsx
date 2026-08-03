"use client";
import { useEffect, useRef, useState } from "react";
import { useReveal } from "@/lib/useReveal";

const SUGGESTION = `function createAI() {
  return PedroIA;
}`;

export default function CopilotDemo() {
  const ref = useReveal<HTMLElement>();
  const box = useRef<HTMLDivElement>(null);
  const [ghost, setGhost] = useState("");

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          let i = 0;
          const id = setInterval(() => {
            setGhost(SUGGESTION.slice(0, i++));
            if (i > SUGGESTION.length) clearInterval(id);
          }, 40);
        }
      },
      { threshold: 0.4 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <section ref={ref} className="relative border-t border-white/5 py-28">
      <div className="mx-auto max-w-5xl px-6 text-center">
        <p data-reveal className="text-sm font-semibold uppercase tracking-widest text-neon">Experiência igual ao Copilot</p>
        <h2 data-reveal className="mx-auto mt-3 max-w-2xl font-display text-4xl font-bold sm:text-5xl">
          Autocomplete que <span className="text-gradient">pensa junto com você.</span>
        </h2>
        <p data-reveal className="mx-auto mt-4 max-w-xl text-frost/60">
          A mesma sensação de GitHub Copilot, Claude Code e Cursor — sugestões inline, aceitas com <kbd className="rounded bg-white/10 px-2 py-0.5 text-xs">Tab</kbd>.
        </p>

        <div ref={box} data-reveal className="mx-auto mt-12 max-w-2xl overflow-hidden rounded-2xl border border-white/10 bg-panel/80 text-left shadow-2xl glow">
          <div className="flex items-center gap-2 border-b border-white/5 px-4 py-3">
            <span className="h-3 w-3 rounded-full bg-red-400/80" />
            <span className="h-3 w-3 rounded-full bg-yellow-400/80" />
            <span className="h-3 w-3 rounded-full bg-green-400/80" />
            <span className="ml-3 text-xs text-frost/40">ai.ts — PedroIA</span>
          </div>
          <pre className="min-h-[150px] p-6 font-mono text-sm leading-relaxed">
            <span className="text-frost/40">{"// digite e o PedroIA sugere...\n"}</span>
            <span className="text-neon/90">{ghost}</span>
            <span className="animate-blink text-neon">▍</span>
          </pre>
        </div>
      </div>
    </section>
  );
}
