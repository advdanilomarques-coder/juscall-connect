import { FormEvent, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import Logo from "../Logo";
import { api, ChatMessage } from "../api";
import { useAuth } from "../auth";

function escapeHtml(s: string) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c] as string));
}
function renderMarkdown(text: string) {
  const parts = text.split(/```/);
  let html = "";
  parts.forEach((p, i) => {
    if (i % 2 === 1) {
      html += `<pre><code>${escapeHtml(p.replace(/^[a-zA-Z0-9_+-]*\n/, ""))}</code></pre>`;
    } else {
      html += escapeHtml(p).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\n/g, "<br/>");
    }
  });
  return html;
}

export default function Chat() {
  const { session, signOut } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef<HTMLDivElement>(null);
  const sessionId = `web-${session?.email || "anon"}`;

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy || !session) return;
    setError("");
    const next = [...messages, { role: "user", content: text } as ChatMessage];
    setMessages(next);
    setInput("");
    setBusy(true);
    try {
      const r = await api.chat(next, session.token, sessionId);
      setMessages([...next, { role: "assistant", content: r.content }]);
    } catch (err: any) {
      setError(err.message || "Erro ao enviar.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app">
      <header className="app-nav">
        <Link to="/" className="brand"><Logo size={26} /><span>Clean Code</span></Link>
        <div className="app-nav-right">
          <span className="who">{session?.displayName || session?.email}</span>
          <button className="btn-ghost sm" onClick={signOut}>Sair</button>
        </div>
      </header>

      <div className="chat-wrap">
        <div className="chat-scroll">
          {messages.length === 0 && (
            <div className="chat-empty">
              <Logo size={54} />
              <h2>Olá! Como posso ajudar? 👋</h2>
              <p>Peça um código, cole um erro, ou pergunte o que quiser. Suas conversas ficam salvas.</p>
              <div className="suggest">
                {["Crie uma função de login em Python", "Explique async/await", "Como reverter um commit no git?"].map((s) => (
                  <button key={s} onClick={() => setInput(s)}>{s}</button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`} dangerouslySetInnerHTML={{ __html: renderMarkdown(m.content) }} />
          ))}
          {busy && <div className="bubble assistant thinking">Clean Code está pensando…</div>}
          {error && <div className="bubble error">⚠️ {error}</div>}
          <div ref={endRef} />
        </div>

        <form className="composer" onSubmit={send}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send(e as unknown as FormEvent);
              }
            }}
            rows={1}
            placeholder="Pergunte ao Clean Code…  (Enter envia, Shift+Enter nova linha)"
          />
          <button className="btn-primary" disabled={busy || !input.trim()}>➤</button>
        </form>
      </div>
    </div>
  );
}
