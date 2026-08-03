"use client";
import { useReveal } from "@/lib/useReveal";

const CARDS = [
  { icon: "🧠", title: "Código Inteligente", desc: "Compreende seu projeto inteiro." },
  { icon: "⚙️", title: "Criação Automática", desc: "Cria arquivos, pastas e estruturas completas." },
  { icon: "🛡️", title: "Correção Avançada", desc: "Encontra erros antes que eles aconteçam." },
  { icon: "🌐", title: "Multilinguagem", desc: "Python, JavaScript, Java, C++, Rust e muito mais." },
];

export default function PowerCards() {
  const ref = useReveal<HTMLElement>();
  return (
    <section ref={ref} id="poder" className="relative border-t border-white/5 py-28">
      <div className="mx-auto max-w-7xl px-6">
        <p data-reveal className="text-sm font-semibold uppercase tracking-widest text-neon">O poder do PedroIA</p>
        <h2 data-reveal className="mt-3 max-w-2xl font-display text-4xl font-bold sm:text-5xl">
          Tudo que um engenheiro sênior faz — <span className="text-gradient">na velocidade da IA.</span>
        </h2>
        <div className="mt-14 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {CARDS.map((c) => (
            <div
              key={c.title}
              data-reveal
              className="group rounded-2xl border border-white/10 bg-panel/60 p-7 transition hover:-translate-y-2 hover:border-neon/40 hover:glow"
            >
              <div className="grid h-12 w-12 place-items-center rounded-xl text-2xl"
                style={{ background: "linear-gradient(135deg,rgba(124,58,237,.25),rgba(34,211,238,.25))" }}>
                {c.icon}
              </div>
              <h3 className="mt-5 font-display text-xl font-semibold">{c.title}</h3>
              <p className="mt-2 text-sm text-frost/60">{c.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
