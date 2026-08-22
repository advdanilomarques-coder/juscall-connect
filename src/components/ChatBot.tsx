import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageCircle, X, Send, Scale, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

const CHAT_ENDPOINT = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/chat`;

const WELCOME: ChatMessage = {
  role: "assistant",
  content:
    "Olá! Sou a Ju, assistente virtual do JusCall. 👋\n\nPosso te ajudar com:\n\n• 🇵🇹 Visto para Portugal\n• 💰 Juros abusivos em contratos\n• 🚗 Financiamento de veículo / busca e apreensão\n\nQual é a sua situação?",
};

const QUICK_REPLIES = [
  "Quero tirar visto para Portugal",
  "Estou pagando juros abusivos",
  "Recebi busca e apreensão do meu carro",
];

const ChatBot = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, open]);

  const sendMessage = async (text: string) => {
    const content = text.trim();
    if (!content || loading) return;

    const history = [...messages, { role: "user", content } as ChatMessage];
    setMessages([...history, { role: "assistant", content: "" }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(CHAT_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          apikey: import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY,
        },
        // Não enviamos a mensagem de boas-vindas fixa para a IA.
        body: JSON.stringify({ messages: history.filter((m) => m !== WELCOME) }),
      });

      if (!res.ok || !res.body) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Não foi possível conectar ao assistente.");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let assistantText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data:")) continue;
          const payload = trimmed.slice(5).trim();
          if (payload === "[DONE]") continue;
          try {
            const json = JSON.parse(payload);
            const delta = json.choices?.[0]?.delta?.content;
            if (delta) {
              assistantText += delta;
              setMessages((prev) => {
                const next = [...prev];
                next[next.length - 1] = { role: "assistant", content: assistantText };
                return next;
              });
            }
          } catch {
            // linha SSE incompleta — ignora
          }
        }
      }

      if (!assistantText) {
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = {
            role: "assistant",
            content: "Desculpe, não consegui responder agora. Tente novamente em instantes.",
          };
          return next;
        });
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Erro inesperado.";
      setMessages((prev) => {
        const next = [...prev];
        next[next.length - 1] = {
          role: "assistant",
          content: `⚠️ ${msg}`,
        };
        return next;
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <>
      {/* Botão flutuante */}
      <button
        aria-label={open ? "Fechar chat" : "Abrir chat de atendimento"}
        onClick={() => setOpen((v) => !v)}
        className={cn(
          "fixed bottom-5 right-5 z-50 flex h-14 w-14 items-center justify-center rounded-full",
          "bg-primary text-primary-foreground shadow-lg transition-transform hover:scale-105",
        )}
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </button>

      {/* Janela do chat */}
      {open && (
        <Card
          className={cn(
            "fixed bottom-24 right-5 z-50 flex flex-col overflow-hidden shadow-2xl",
            "w-[calc(100vw-2.5rem)] max-w-sm h-[70vh] max-h-[560px]",
          )}
        >
          {/* Cabeçalho */}
          <div className="flex items-center gap-3 border-b border-border bg-primary px-4 py-3 text-primary-foreground">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-foreground/15">
              <Scale className="h-5 w-5" />
            </div>
            <div className="leading-tight">
              <p className="font-semibold">Ju · Assistente JusCall</p>
              <p className="text-xs opacity-90">Vistos · Juros · Financiamento</p>
            </div>
          </div>

          {/* Mensagens */}
          <ScrollArea className="flex-1">
            <div ref={scrollRef} className="flex flex-col gap-3 p-4">
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={cn(
                    "max-w-[85%] whitespace-pre-wrap rounded-2xl px-3.5 py-2.5 text-sm",
                    m.role === "user"
                      ? "self-end bg-primary text-primary-foreground rounded-br-sm"
                      : "self-start bg-muted text-foreground rounded-bl-sm",
                  )}
                >
                  {m.content ||
                    (loading && i === messages.length - 1 ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      ""
                    ))}
                </div>
              ))}

              {/* Sugestões rápidas (só no início) */}
              {messages.length === 1 && (
                <div className="mt-1 flex flex-col gap-2">
                  {QUICK_REPLIES.map((q) => (
                    <button
                      key={q}
                      onClick={() => sendMessage(q)}
                      className="rounded-xl border border-border bg-card px-3 py-2 text-left text-sm text-foreground transition-colors hover:bg-muted"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Entrada */}
          <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t border-border p-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Digite sua mensagem..."
              disabled={loading}
              className="flex-1"
            />
            <Button type="submit" size="icon" disabled={loading || !input.trim()}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </form>

          <p className="px-3 pb-2 text-center text-[10px] leading-tight text-muted-foreground">
            Orientações gerais. Não substitui a consulta com um advogado.
          </p>
        </Card>
      )}
    </>
  );
};

export default ChatBot;
