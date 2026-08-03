"use client";
import { useReveal } from "@/lib/useReveal";
import { GITHUB_URL, DOCS_URL } from "@/lib/links";

const ITEMS = [
  { icon: "🐙", t: "GitHub", d: "Código aberto e contribuições." },
  { icon: "📚", t: "Documentação", d: "Guias, exemplos e referência." },
  { icon: "💬", t: "Comunidade", d: "Troque ideias com outros devs." },
  { icon: "🚀", t: "Atualizações", d: "Novidades a cada release." },
];

export default function Community() {
  const ref = useReveal<HTMLElement>();
  return (
    <section ref={ref} id="comunidade" className="relative border-t border-white/5 py-28">
      <div className="mx-auto max-w-6xl px-6">
        <h2 data-reveal className="text-center font-display text-4xl font-bold sm:text-5xl">
          Comunidade <span className="text-gradient">PedroIA</span>
        </h2>
        <div className="mt-14 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {ITEMS.map((i) => (
            <div key={i.t} data-reveal className="rounded-2xl border border-white/10 bg-panel/60 p-7">
              <div className="text-3xl">{i.icon}</div>
              <h3 className="mt-4 font-display text-lg font-semibold">{i.t}</h3>
              <p className="mt-1 text-sm text-frost/60">{i.d}</p>
            </div>
          ))}
        </div>
        <div data-reveal className="mt-12 flex flex-wrap justify-center gap-4">
          <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="btn-ghost">Ver código</a>
          <a href={DOCS_URL} target="_blank" rel="noopener noreferrer" className="btn-primary">Entrar na comunidade</a>
        </div>
      </div>
    </section>
  );
}
