"use client";
import { useReveal } from "@/lib/useReveal";

export default function HybridIntel() {
  const ref = useReveal<HTMLElement>();
  const nodes = [
    { label: "Modelos locais", x: "12%", y: "30%" },
    { label: "Modelos avançados", x: "80%", y: "22%" },
    { label: "Conhecimento profissional", x: "78%", y: "74%" },
    { label: "Seu projeto", x: "16%", y: "72%" },
  ];
  return (
    <section ref={ref} className="relative border-t border-white/5 py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="text-center">
          <p data-reveal className="text-sm font-semibold uppercase tracking-widest text-neon">Inteligência híbrida</p>
          <h2 data-reveal className="mx-auto mt-3 max-w-2xl font-display text-4xl font-bold sm:text-5xl">
            Online ou offline, <span className="text-gradient">PedroIA continua trabalhando.</span>
          </h2>
        </div>

        <div data-reveal className="relative mx-auto mt-16 h-[360px] max-w-3xl">
          {/* núcleo */}
          <div className="absolute left-1/2 top-1/2 grid h-24 w-24 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full text-3xl glow"
            style={{ background: "radial-gradient(circle,#7c3aed,#22d3ee)" }}>
            🧠
          </div>
          {/* rede */}
          <svg className="absolute inset-0 h-full w-full" aria-hidden>
            {nodes.map((n) => (
              <line key={n.label} x1="50%" y1="50%" x2={n.x} y2={n.y} stroke="url(#g)" strokeWidth="1.5" opacity="0.5" />
            ))}
            <defs>
              <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#7c3aed" />
                <stop offset="100%" stopColor="#22d3ee" />
              </linearGradient>
            </defs>
          </svg>
          {nodes.map((n) => (
            <div key={n.label} className="absolute -translate-x-1/2 -translate-y-1/2" style={{ left: n.x, top: n.y }}>
              <div className="rounded-full border border-white/10 bg-panel/80 px-4 py-2 text-sm text-frost/80 backdrop-blur">
                {n.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
