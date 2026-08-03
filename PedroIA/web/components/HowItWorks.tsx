"use client";
import { useReveal } from "@/lib/useReveal";

const STEPS = [
  { n: "01", t: "Instale a extensão", d: "Um clique no Marketplace do VS Code." },
  { n: "02", t: "Abra seu projeto", d: "O PedroIA lê e entende o contexto." },
  { n: "03", t: "Converse com PedroIA", d: "Peça, pergunte, refatore — em linguagem natural." },
  { n: "04", t: "Construa qualquer software", d: "Do protótipo ao deploy, ao seu lado." },
];

export default function HowItWorks() {
  const ref = useReveal<HTMLElement>();
  return (
    <section ref={ref} id="como" className="relative border-t border-white/5 py-28">
      <div className="mx-auto max-w-5xl px-6">
        <h2 data-reveal className="text-center font-display text-4xl font-bold sm:text-5xl">
          Como <span className="text-gradient">funciona</span>
        </h2>
        <div className="mt-16 space-y-2">
          {STEPS.map((s, i) => (
            <div key={s.n} data-reveal className="flex items-start gap-6">
              <div className="flex flex-col items-center">
                <span className="grid h-14 w-14 shrink-0 place-items-center rounded-full border border-neon/40 font-display text-lg font-bold text-neon">
                  {s.n}
                </span>
                {i < STEPS.length - 1 && <span className="my-1 h-16 w-px bg-gradient-to-b from-neon/50 to-transparent" />}
              </div>
              <div className="pt-3">
                <h3 className="font-display text-2xl font-semibold">{s.t}</h3>
                <p className="mt-1 text-frost/60">{s.d}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
