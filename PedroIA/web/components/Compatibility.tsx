"use client";
import { useReveal } from "@/lib/useReveal";

const TOOLS = [
  { name: "VS Code", first: true },
  { name: "IntelliJ", first: false },
  { name: "PyCharm", first: false },
  { name: "JetBrains", first: false },
];

export default function Compatibility() {
  const ref = useReveal<HTMLElement>();
  return (
    <section ref={ref} className="relative border-t border-white/5 py-28">
      <div className="mx-auto max-w-6xl px-6 text-center">
        <h2 data-reveal className="font-display text-4xl font-bold sm:text-5xl">
          Compatibilidade
        </h2>
        <p data-reveal className="mt-3 text-frost/60">
          <span className="text-gradient font-semibold">VS Code First</span> — com o ecossistema que você já usa.
        </p>
        <div className="mt-14 grid grid-cols-2 gap-5 sm:grid-cols-4">
          {TOOLS.map((t) => (
            <div
              key={t.name}
              data-reveal
              className={`rounded-2xl border p-8 font-display text-lg font-semibold transition ${
                t.first
                  ? "border-neon/50 bg-neon/5 text-frost glow"
                  : "border-white/10 bg-panel/50 text-frost/60"
              }`}
            >
              {t.name}
              {t.first && <span className="mt-2 block text-xs font-normal text-neon">Suporte total</span>}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
