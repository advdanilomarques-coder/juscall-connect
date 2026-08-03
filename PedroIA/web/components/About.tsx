"use client";
import { useReveal } from "@/lib/useReveal";

const PILLARS = ["Inteligência artificial", "Engenharia de software", "Automação", "Criatividade humana"];

export default function About() {
  const ref = useReveal<HTMLElement>();
  return (
    <section ref={ref} id="sobre" className="relative border-t border-white/5 py-28">
      <div className="mx-auto max-w-4xl px-6 text-center">
        <h2 data-reveal className="font-display text-4xl font-bold sm:text-5xl">
          Construindo o <span className="text-gradient">futuro da programação.</span>
        </h2>
        <p data-reveal className="mx-auto mt-6 max-w-2xl text-lg text-frost/70">
          O PedroIA nasceu para transformar desenvolvedores em arquitetos de soluções. Ele une o melhor
          da máquina e do humano em um só fluxo de trabalho.
        </p>
        <div className="mt-12 flex flex-wrap justify-center gap-3">
          {PILLARS.map((p) => (
            <span key={p} data-reveal className="rounded-full border border-white/10 bg-panel/60 px-5 py-2.5 text-sm text-frost/80">
              {p}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
