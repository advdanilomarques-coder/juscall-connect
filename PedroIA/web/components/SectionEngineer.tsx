"use client";
import { useEffect, useRef, useState } from "react";
import { useReveal } from "@/lib/useReveal";

const STEPS = [
  "Analisando projeto...",
  "Entendendo arquitetura...",
  "Criando solução...",
  "Código otimizado. ✅",
];

export default function SectionEngineer() {
  const ref = useReveal<HTMLElement>();
  const [active, setActive] = useState(0);
  const panel = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = panel.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          let i = 0;
          const id = setInterval(() => {
            setActive(++i);
            if (i >= STEPS.length) clearInterval(id);
          }, 900);
        }
      },
      { threshold: 0.4 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <section ref={ref} id="engenheiro" className="relative border-t border-white/5 py-28">
      <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-14 px-6 lg:grid-cols-2">
        <div>
          <h2 data-reveal className="font-display text-4xl font-bold leading-tight sm:text-5xl">
            Não é apenas uma IA.
            <br />
            <span className="text-gradient">É um engenheiro trabalhando ao seu lado.</span>
          </h2>
          <p data-reveal className="mt-6 max-w-lg text-frost/70">
            Enquanto você escreve, o PedroIA lê o projeto inteiro, entende a arquitetura e propõe
            a solução — no seu ritmo, dentro do seu editor.
          </p>
        </div>

        <div ref={panel} data-reveal className="rounded-2xl border border-white/10 bg-panel/70 p-6 font-mono text-sm glow">
          {STEPS.map((s, i) => (
            <div
              key={s}
              className={`flex items-center gap-3 py-2 transition ${
                i < active ? "text-neon" : "text-frost/25"
              }`}
            >
              <span className={`h-2 w-2 rounded-full ${i < active ? "bg-neon" : "bg-frost/20"}`} />
              {s}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
