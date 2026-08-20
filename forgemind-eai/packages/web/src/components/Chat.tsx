import { useEffect, useRef, useState } from "react";
import { api, type ChatMessage } from "../api.js";
import { IconSend } from "./icons.js";

const SUGGESTIONS = [
  "Explique o que este projeto faz",
  "Como criar uma API REST em Node?",
  "localhost",
  "Me ajude a debugar um erro",
];

export function Chat({ site }: { site: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, streaming]);

  async function send(text: string) {
    const q = text.trim();
    if (!q || streaming) return;

    // Atalho local: "localhost" devolve a URL do site sem chamar a IA.
    if (q.toLowerCase() === "localhost" || q.toLowerCase() === "/site") {
      setMessages((m) => [
        ...m,
        { role: "user", content: q },
        { role: "assistant", content: `Seu site ForgeMind (local, só seu):\n\n${site}\n\nAbra no navegador para conversar por aqui também.` },
      ]);
      setInput("");
      return;
    }

    const next: ChatMessage[] = [...messages, { role: "user", content: q }];
    setMessages(next);
    setInput("");
    setStreaming(true);
    setMessages((m) => [...m, { role: "assistant", content: "" }]);

    const controller = new AbortController();
    abortRef.current = controller;
    try {
      await api.chat(
        next,
        (delta) => {
          setMessages((m) => {
            const copy = [...m];
            copy[copy.length - 1] = { role: "assistant", content: copy[copy.length - 1]!.content + delta };
            return copy;
          });
        },
        controller.signal,
      );
    } catch (e) {
      setMessages((m) => {
        const copy = [...m];
        copy[copy.length - 1] = { role: "assistant", content: `[erro de conexão] ${(e as Error).message}` };
        return copy;
      });
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }

  function onKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  }

  return (
    <>
      <div className="chat-scroll" ref={scrollRef}>
        {messages.length === 0 ? (
          <div className="empty">
            <div className="hero">◆</div>
            <h2>ForgeMind EAI</h2>
            <p>Sua IA de desenvolvimento local e offline. Pergunte sobre código, terminal, arquitetura — ou o que quiser.</p>
            <div className="suggest">
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => send(s)}>{s}</button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat-inner">
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                <div className="avatar">{m.role === "user" ? "eu" : "◆"}</div>
                <div className="bubble">
                  <div className="who">{m.role === "user" ? "Você" : "ForgeMind"}</div>
                  <span className={streaming && i === messages.length - 1 && m.role === "assistant" ? "cursor" : ""}>
                    {m.content}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="composer">
        <div className="composer-inner">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKey}
            placeholder="Fale com o ForgeMind…  (Enter envia, Shift+Enter quebra linha)"
            rows={1}
          />
          <button className="send" disabled={streaming || !input.trim()} onClick={() => send(input)}>
            <IconSend width={16} height={16} />
          </button>
        </div>
        <div className="hint">100% local • nada sai da sua máquina • digite “localhost” para abrir seu site</div>
      </div>
    </>
  );
}
