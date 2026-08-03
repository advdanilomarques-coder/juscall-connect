"use client";
import { useReveal } from "@/lib/useReveal";
import { MARKETPLACE_URL } from "@/lib/links";

export default function FinalCTA() {
  const ref = useReveal<HTMLElement>();
  return (
    <section ref={ref} className="relative flex min-h-screen items-center justify-center overflow-hidden border-t border-white/5 grid-bg">
      <div className="absolute inset-0 -z-10"
        style={{ background: "radial-gradient(60% 60% at 50% 50%, rgba(124,58,237,.25), transparent 70%)" }} />
      <div className="mx-auto max-w-3xl px-6 text-center">
        <h2 data-reveal className="font-display text-5xl font-bold leading-tight sm:text-7xl">
          O futuro do desenvolvimento <span className="text-gradient">começou.</span>
        </h2>
        <div data-reveal className="mt-12">
          <a
            href={MARKETPLACE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary text-lg sm:text-xl"
            style={{ padding: "1.25rem 2.5rem" }}
          >
            ⬇ Instalar PedroIA no VS Code
          </a>
        </div>
      </div>
    </section>
  );
}
