import { useEffect, useRef, useState, type ReactNode } from "react";
import type { Info } from "../api.js";
import "../landing.css";

/**
 * Landing profissional do ForgeMind — tela inicial (rolagem longa com reveal).
 * 100% offline: arte em SVG/CSS. Fotos reais opcionais em /img/<nome>.jpg
 * (soltando o arquivo em packages/web/public/img/); sem foto, cai na arte.
 */
export function Landing({ info, onEnter }: { info: Info | null; onEnter: () => void }) {
  const provider = info?.provider ?? "heuristic";
  return (
    <div className="lp">
      <ForgeBackdrop />
      <Nav onEnter={onEnter} />

      {/* HERO */}
      <header className="lp-hero">
        <div className="lp-hero-inner">
          <span className="lp-eyebrow">IA pessoal de engenharia • local‑first</span>
          <h1 className="lp-title">
            Sua IA de desenvolvimento,<br />
            <span className="lp-grad">forjada na sua máquina.</span>
          </h1>
          <p className="lp-sub">
            ForgeMind entende o seu projeto inteiro, completa código com Ghost Text contextual,
            explica o terminal e conversa — rodando <b>offline</b> quando você quer, e com a
            nuvem só quando faz sentido.
          </p>
          <div className="lp-cta">
            <button className="btn-primary lg" onClick={onEnter}>Entrar no ForgeMind →</button>
            <a className="btn-ghost lg" href="#capacidades">Ver capacidades</a>
          </div>
          <div className="lp-badges">
            <Badge dot={info?.offline ? "on" : "off"}>{info?.offline ? "Rodando offline" : "Online"}</Badge>
            <Badge>provider: {provider}</Badge>
            <Badge>Node 20 • SQLite • sem Ollama</Badge>
          </div>
        </div>
        <div className="lp-hero-art"><CodeWindow /></div>
      </header>

      {/* MARQUEE — "scroll roll" infinito de tecnologias */}
      <Marquee />

      {/* CAPACIDADES */}
      <section id="capacidades" className="lp-section">
        <SectionHead kicker="O que ele faz" title="Feito para projetos grandes de verdade" />
        <div className="lp-features">
          <Feature icon={<GlyphInline />} title="Ghost Text / Inline contextual"
            reveal photo="inline">
            Completions de uma linha a blocos inteiros, com <b>contexto cruzado</b> entre arquivos
            (imports e dependências). Debounce, cache e cancelamento — leve, nunca a cada tecla.
          </Feature>
          <Feature icon={<GlyphGraph />} title="Agente de projetos grandes" reveal photo="agent">
            Indexação incremental de ~100k linhas: símbolos, tipos, rotas e grafo de dependências.
            Ele recupera só o relevante e responde sobre a base inteira.
          </Feature>
          <Feature icon={<GlyphTerminal />} title="Terminal AI" reveal photo="terminal">
            Explica, sugere e corrige comandos com Ghost Text no shell. Nunca executa nada
            perigoso sozinho — confirmação sempre.
          </Feature>
          <Feature icon={<GlyphMemory />} title="Memória & histórico" reveal photo="memory">
            Conversa, projeto e histórico em SQLite local — pesquisável, exportável e apagável.
            Seus dados ficam com você.
          </Feature>
          <Feature icon={<GlyphShield />} title="Privado e offline" reveal photo="privacy">
            Núcleo roda sem internet. Redaction de segredos: nunca envia <code>.env</code>, chaves
            ou tokens. Você controla o que sai da máquina.
          </Feature>
          <Feature icon={<GlyphSpark />} title="Híbrido inteligente" reveal photo="hybrid">
            Chat forte com Gemini quando online; Ghost Text sempre local e rápido. Troca de
            provider sem tocar no núcleo.
          </Feature>
        </div>
      </section>

      {/* STATS */}
      <Stats />

      {/* COMO FUNCIONA */}
      <section className="lp-section">
        <SectionHead kicker="Arquitetura" title="Um núcleo, três interfaces" />
        <div className="lp-flow">
          <FlowNode label="Terminal (CLI)" sub="conversa estilo Claude Code" />
          <FlowArrow />
          <FlowNode label="Backend local" sub="Fastify • SQLite • índice" highlight />
          <FlowArrow />
          <FlowNode label="Site & Extensão" sub="este site + VS Code" />
        </div>
        <p className="lp-flow-note">
          A chave da API nunca vai ao frontend — toda chamada externa passa pelo backend local.
        </p>
      </section>

      {/* CTA FINAL */}
      <section className="lp-final">
        <div className="lp-final-card">
          <h2>Pronto para forjar?</h2>
          <p>Entre no seu ForgeMind e comece a conversar, indexar e completar código.</p>
          <button className="btn-primary lg" onClick={onEnter}>Entrar no ForgeMind →</button>
        </div>
      </section>

      <footer className="lp-footer">
        <span>◆ ForgeMind EAI</span>
        <span>local‑first • offline • {new Date().getFullYear()}</span>
      </footer>
    </div>
  );
}

/* ---------------- reveal on scroll ---------------- */
function useReveal<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [seen, setSeen] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === "undefined") {
      setSeen(true); // sem suporte: mostra tudo (nunca fica invisivel)
      return;
    }
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && (setSeen(true), io.disconnect())),
      { threshold: 0.15 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return { ref, seen };
}

/* ---------------- blocos ---------------- */
function Nav({ onEnter }: { onEnter: () => void }) {
  return (
    <nav className="lp-nav">
      <div className="lp-nav-brand"><span className="lp-mark">◆</span> ForgeMind</div>
      <div className="lp-nav-links">
        <a href="#capacidades">Capacidades</a>
        <button className="btn-primary sm" onClick={onEnter}>Entrar</button>
      </div>
    </nav>
  );
}

function SectionHead({ kicker, title }: { kicker: string; title: string }) {
  const { ref, seen } = useReveal<HTMLDivElement>();
  return (
    <div ref={ref} className={`lp-head reveal ${seen ? "in" : ""}`}>
      <span className="lp-kicker">{kicker}</span>
      <h2>{title}</h2>
    </div>
  );
}

function Feature({
  icon, title, children, reveal, photo,
}: { icon: ReactNode; title: string; children: ReactNode; reveal?: boolean; photo?: string }) {
  const { ref, seen } = useReveal<HTMLDivElement>();
  return (
    <article ref={ref} className={`lp-card ${reveal ? "reveal" : ""} ${seen ? "in" : ""}`}>
      <div className="lp-card-visual">
        <Photo name={photo} />
        <div className="lp-card-icon">{icon}</div>
      </div>
      <h3>{title}</h3>
      <p>{children}</p>
    </article>
  );
}

/** Foto real opcional (/img/<name>.jpg). Sem arquivo, some e fica só a arte. */
function Photo({ name }: { name?: string }) {
  const [ok, setOk] = useState(true);
  if (!name || !ok) return null;
  return (
    <img className="lp-photo" src={`/img/${name}.jpg`} alt="" loading="lazy" onError={() => setOk(false)} />
  );
}

function Badge({ children, dot }: { children: ReactNode; dot?: "on" | "off" }) {
  return (
    <span className="lp-badge">
      {dot && <span className={`lp-dot ${dot}`} />}
      {children}
    </span>
  );
}

function Marquee() {
  const items = [
    "TypeScript", "Python", "Rust", "Go", "React", "FastAPI", "SQLite", "Node 20",
    "Ghost Text", "FIM", "RAG", "Embeddings", "Vite", "SQLAlchemy", "Java", "C++",
    "Kotlin", "Swift", "GraphQL", "Docker", "Git", "Vue", "Svelte", "Bash",
  ];
  const row = [...items, ...items];
  return (
    <div className="lp-marquee" aria-hidden>
      <div className="lp-marquee-track">
        {row.map((t, i) => (
          <span key={i} className="lp-chip">{t}</span>
        ))}
      </div>
    </div>
  );
}

function Stats() {
  const { ref, seen } = useReveal<HTMLDivElement>();
  const stats = [
    ["~100k", "linhas indexáveis"],
    ["0", "dados enviados sem você querer"],
    ["∞", "requisições no modo local"],
    ["3", "interfaces: CLI, site, extensão"],
  ];
  return (
    <div ref={ref} className={`lp-stats reveal ${seen ? "in" : ""}`}>
      {stats.map(([n, l]) => (
        <div key={l} className="lp-stat">
          <div className="lp-stat-n">{n}</div>
          <div className="lp-stat-l">{l}</div>
        </div>
      ))}
    </div>
  );
}

function FlowNode({ label, sub, highlight }: { label: string; sub: string; highlight?: boolean }) {
  return (
    <div className={`lp-flow-node ${highlight ? "hl" : ""}`}>
      <div className="lp-flow-label">{label}</div>
      <div className="lp-flow-sub">{sub}</div>
    </div>
  );
}
function FlowArrow() {
  return <div className="lp-flow-arrow">→</div>;
}

/* ---------------- arte SVG (offline) ---------------- */
function ForgeBackdrop() {
  return (
    <div className="lp-backdrop" aria-hidden>
      <div className="lp-glow g1" />
      <div className="lp-glow g2" />
      <div className="lp-grid" />
    </div>
  );
}

function CodeWindow() {
  const { ref, seen } = useReveal<HTMLDivElement>();
  return (
    <div ref={ref} className={`lp-code reveal ${seen ? "in" : ""}`}>
      <div className="lp-code-bar">
        <i /><i /><i /><span>forgemind · inline</span>
      </div>
      <pre className="lp-code-body">
{`function ranquear(sintomas: `}<span className="t">Sintoma[]</span>{`) {
  `}<span className="k">const</span>{` score = sintomas.`}<span className="f">reduce</span>{`(
    (`}<span className="p">acc, s</span>{`) => acc + peso(s), 0);`}
        <span className="ghost">{`
  return score > LIMIAR ? "urgente" : "rotina"; // ← Ghost Text`}</span>{`
}`}
      </pre>
    </div>
  );
}

const S = { width: 26, height: 26, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.7, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
const GlyphInline = () => (<svg {...S}><path d="M8 6 3 12l5 6" /><path d="m16 6 5 6-5 6" /><path d="M13 4l-2 16" /></svg>);
const GlyphGraph = () => (<svg {...S}><circle cx="5" cy="6" r="2" /><circle cx="19" cy="6" r="2" /><circle cx="12" cy="18" r="2" /><path d="M6.7 7.3 10.6 16M17.3 7.3 13.4 16M7 6h10" /></svg>);
const GlyphTerminal = () => (<svg {...S}><rect x="3" y="4" width="18" height="16" rx="2" /><path d="m7 9 3 3-3 3M13 15h4" /></svg>);
const GlyphMemory = () => (<svg {...S}><rect x="4" y="4" width="16" height="16" rx="2" /><path d="M9 4v16M15 4v16M4 9h5M4 15h5M15 9h5M15 15h5" /></svg>);
const GlyphShield = () => (<svg {...S}><path d="M12 3l7 3v6c0 4-3 7-7 9-4-2-7-5-7-9V6z" /><path d="m9 12 2 2 4-4" /></svg>);
const GlyphSpark = () => (<svg {...S}><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18" /><circle cx="12" cy="12" r="2.5" /></svg>);
