import Logo from "./Logo";

const FEATURES = [
  { icon: "💬", title: "Chat integrado", desc: "Converse com um engenheiro sênior sem sair do editor. Histórico e memória inclusos." },
  { icon: "⚡", title: "Autocomplete", desc: "Sugestões inline enquanto você digita — no estilo Copilot, com seu próprio motor." },
  { icon: "🛠️", title: "Comandos", desc: "/create, /fix, /explain, /refactor, /test e /security direto no menu de contexto." },
  { icon: "🧠", title: "Contexto automático", desc: "Lê o arquivo ativo, a seleção e os erros. Sem prompts gigantes." },
  { icon: "🔌", title: "Multi-LLM", desc: "Claude, OpenAI, Gemini, DeepSeek e modelos locais via Ollama." },
  { icon: "📴", title: "Funciona offline", desc: "Online usa a nuvem; sem internet, cai para o modelo local automaticamente." },
];

const STEPS = [
  { n: "1", t: "Instale", d: "Rode bash install.sh — backend, banco e extensão prontos." },
  { n: "2", t: "Configure", d: "Adicione uma chave de nuvem ou instale o Ollama para modo offline." },
  { n: "3", t: "Programe", d: "Abra o VS Code e chame o PedroIA na barra lateral." },
];

export default function App() {
  return (
    <div className="page">
      <header className="nav">
        <div className="brand">
          <Logo size={32} />
          <span>PedroIA</span>
        </div>
        <nav>
          <a href="#features">Recursos</a>
          <a href="#how">Como usar</a>
          <a href="https://github.com/advdanilomarques-coder/juscall-connect" className="btn-ghost">GitHub</a>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-glow" aria-hidden />
          <Logo size={84} />
          <h1>
            PedroIA — Seu <span className="grad">engenheiro de IA</span> dentro do VS Code
          </h1>
          <p className="sub">
            Entende seu projeto, cria código, corrige erros, escreve testes e refatora.
            Online ou offline. Um engenheiro sênior no seu editor.
          </p>
          <div className="cta">
            <a className="btn-primary" href="#how">⬇ Baixar extensão</a>
            <a className="btn-ghost" href="#features">Ver recursos</a>
          </div>
          <div className="chips">
            <span>Claude</span><span>OpenAI</span><span>Gemini</span><span>DeepSeek</span><span>Ollama</span>
          </div>
        </section>

        <section id="features" className="features">
          <h2>Tudo o que um dev sênior faz</h2>
          <div className="grid">
            {FEATURES.map((f) => (
              <article key={f.title} className="card">
                <div className="card-icon">{f.icon}</div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="how" className="how">
          <h2>Comece em 3 passos</h2>
          <div className="steps">
            {STEPS.map((s) => (
              <div key={s.n} className="step">
                <div className="step-n">{s.n}</div>
                <h3>{s.t}</h3>
                <p>{s.d}</p>
              </div>
            ))}
          </div>
          <pre className="install">
            <code>git clone … &amp;&amp; cd PedroIA{"\n"}bash install.sh</code>
          </pre>
        </section>
      </main>

      <footer className="footer">
        <Logo size={24} />
        <span>PedroIA · MIT License · Feito para desenvolvedores</span>
      </footer>
    </div>
  );
}
