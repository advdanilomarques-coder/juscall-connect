import { useEffect } from "react";
import { Link } from "react-router-dom";
import Logo from "../Logo";
import { useAuth } from "../auth";
import { VSCODE_MARKETPLACE_URL, GITHUB_URL } from "../config";

const FEATURES = [
  { icon: "⚡", title: "Autocomplete inline", desc: "Sugestões calmas em tempo real enquanto você digita, no estilo Copilot. É o coração do Clean Code." },
  { icon: "💬", title: "Chat com contexto", desc: "Converse e resolva dúvidas com memória da conversa, direto no editor." },
  { icon: "🧠", title: "Entende seu projeto", desc: "Lê o arquivo, a seleção e os erros automaticamente. Sem prompts gigantes." },
  { icon: "🛠️", title: "13+ comandos", desc: "Explicar, corrigir, refatorar, documentar, revisar, otimizar, testar, converter e mais." },
  { icon: "💻", title: "Ajuda no terminal", desc: "Leia um erro do terminal e receba o comando exato para resolver." },
  { icon: "🌐", title: "Conhecimentos gerais", desc: "Além de código, tira dúvidas do dia a dia, explica conceitos e ajuda a escrever." },
];

const FAQ = [
  { q: "O Clean Code é só para código?", a: "Não. O foco central é programação — autocomplete, chat e comandos —, mas ele também responde conhecimentos gerais e dúvidas do dia a dia." },
  { q: "Funciona em quais linguagens?", a: "Em praticamente todas: Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, PHP, Kotlin, Swift, SQL e mais." },
  { q: "Preciso pagar?", a: "É grátis para começar. Você pode usar modelos gratuitos na nuvem ou rodar modelos locais." },
  { q: "Meus dados ficam seguros?", a: "O código enviado é processado pelo servidor e pelo modelo de IA configurado. Evite enviar segredos e use um serviço de sua confiança." },
];

const STEPS = [
  { n: "01", t: "Instale a extensão", d: "Adicione o Clean Code ao VS Code com um clique." },
  { n: "02", t: "Conecte-se", d: "Crie sua conta e entre — ou use sua própria chave de modelo." },
  { n: "03", t: "Programe melhor", d: "Chat, autocomplete e comandos trabalhando ao seu lado." },
];

export default function Landing() {
  const { session } = useAuth();

  useEffect(() => {
    const els = document.querySelectorAll("[data-reveal]");
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && e.target.classList.add("in")),
      { threshold: 0.12 }
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  return (
    <div className="site">
      <header className="nav">
        <Link to="/" className="brand">
          <Logo size={30} />
          <span>Clean Code</span>
        </Link>
        <nav className="nav-links">
          <a href="#features">Recursos</a>
          <a href="#how">Como funciona</a>
          <a href="#about">Sobre</a>
          {session ? (
            <Link to="/app" className="btn-primary sm">Abrir chat</Link>
          ) : (
            <>
              <Link to="/login">Entrar</Link>
              <Link to="/signup" className="btn-primary sm">Criar conta</Link>
            </>
          )}
        </nav>
      </header>

      <main>
        {/* Hero */}
        <section className="hero">
          <div className="aurora" aria-hidden />
          <div className="hero-inner" data-reveal>
            <span className="eyebrow">Assistente de IA · VS Code</span>
            <h1>
              Escreva código <span className="grad">limpo</span>,<br /> mais rápido.
            </h1>
            <p className="lead">
              O Clean Code é o seu par de programação com IA: chat com contexto, autocomplete
              inline e comandos que criam, corrigem e refatoram — em qualquer linguagem. E também
              te ajuda no que precisar além do código.
            </p>
            <div className="cta">
              <a className="btn-primary" href={VSCODE_MARKETPLACE_URL} target="_blank" rel="noreferrer">
                Abrir no VS Code →
              </a>
              <Link className="btn-ghost" to={session ? "/app" : "/signup"}>
                {session ? "Abrir o chat" : "Testar pelo site"}
              </Link>
            </div>
            <div className="chips">
              <span>Claude</span><span>GPT</span><span>Gemini</span><span>Groq</span><span>Ollama</span>
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="section">
          <div className="section-head" data-reveal>
            <span className="kicker">Recursos</span>
            <h2>Tudo o que um dev sênior faz — ao seu lado</h2>
          </div>
          <div className="grid">
            {FEATURES.map((f, i) => (
              <article className="card" data-reveal style={{ transitionDelay: `${i * 60}ms` }} key={f.title}>
                <div className="card-icon">{f.icon}</div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </article>
            ))}
          </div>
        </section>

        {/* How */}
        <section id="how" className="section muted">
          <div className="section-head" data-reveal>
            <span className="kicker">Como funciona</span>
            <h2>Do zero ao fluxo em minutos</h2>
          </div>
          <div className="steps">
            {STEPS.map((s, i) => (
              <div className="step" data-reveal style={{ transitionDelay: `${i * 80}ms` }} key={s.n}>
                <span className="step-n">{s.n}</span>
                <h3>{s.t}</h3>
                <p>{s.d}</p>
              </div>
            ))}
          </div>
        </section>

        {/* About */}
        <section id="about" className="section">
          <div className="about" data-reveal>
            <span className="kicker">Mais sobre o Clean Code</span>
            <h2>Feito para acelerar quem cria software</h2>
            <p>
              O Clean Code nasceu para ser um engenheiro de software sênior dentro do seu editor —
              e um assistente inteligente para o que mais você precisar. Ele entende o contexto do
              seu projeto, sugere código enquanto você digita e executa tarefas complexas por
              comando. Tudo com foco em <strong>código limpo</strong>, legível e pronto para produção.
            </p>
            <p>
              Sob o capô, um roteador multi-modelo escolhe a melhor IA disponível: usa a nuvem
              quando há internet e cai para modelos locais quando está offline — então você nunca
              fica sem assistente. Suas conversas ficam com <strong>memória</strong>, para o
              assistente lembrar do contexto ao longo do tempo.
            </p>
            <div className="about-actions">
              <a className="btn-primary" href={VSCODE_MARKETPLACE_URL} target="_blank" rel="noreferrer">Abrir no VS Code</a>
              <a className="btn-ghost" href={GITHUB_URL} target="_blank" rel="noreferrer">Ver no GitHub</a>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" className="section muted">
          <div className="section-head" data-reveal>
            <span className="kicker">Perguntas frequentes</span>
            <h2>Ainda com dúvida?</h2>
          </div>
          <div className="faq">
            {FAQ.map((item, i) => (
              <details className="faq-item" data-reveal style={{ transitionDelay: `${i * 60}ms` }} key={item.q}>
                <summary>{item.q}</summary>
                <p>{item.a}</p>
              </details>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="section cta-band">
          <div className="cta-inner" data-reveal>
            <h2>Pronto para programar com o Clean Code?</h2>
            <p>Grátis para começar. Abra no VS Code ou experimente pelo site.</p>
            <div className="cta">
              <a className="btn-primary" href={VSCODE_MARKETPLACE_URL} target="_blank" rel="noreferrer">Abrir no VS Code →</a>
              <Link className="btn-ghost" to={session ? "/app" : "/signup"}>Testar pelo site</Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="brand"><Logo size={22} /><span>Clean Code</span></div>
        <span className="muted-text">© {new Date().getFullYear()} · Feito para desenvolvedores · MIT</span>
      </footer>
    </div>
  );
}
