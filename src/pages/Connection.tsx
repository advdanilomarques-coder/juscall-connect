import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Scale, Video, MapPin, Send, Phone, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

const MOCK_MESSAGES = [
  { id: 1, sender: "lawyer", text: "Olá, sou o Dr. João Silva. Como posso ajudá-lo?", time: "14:23" },
  { id: 2, sender: "client", text: "Preciso de ajuda urgente. Estou na delegacia.", time: "14:24" },
  { id: 3, sender: "lawyer", text: "Entendo. Vou te orientar agora. Qual é a situação exata?", time: "14:25" },
];

const Connection = () => {
  const [messages, setMessages] = useState(MOCK_MESSAGES);
  const [newMessage, setNewMessage] = useState("");

  const handleSend = () => {
    if (newMessage.trim()) {
      setMessages([
        ...messages,
        {
          id: messages.length + 1,
          sender: "client",
          text: newMessage,
          time: new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
      setNewMessage("");
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-card p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link to="/dashboard/client">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-sm font-semibold">
                JS
              </div>
              <div>
                <p className="font-semibold text-sm">Dr. João Silva</p>
                <p className="text-xs text-accent flex items-center gap-1">
                  <span className="h-2 w-2 rounded-full bg-accent"></span>
                  Online
                </p>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="icon">
              <Phone className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon">
              <Video className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Payment Notice */}
      <div className="bg-muted/50 p-3 border-b border-border">
        <p className="text-xs text-center text-muted-foreground">
          <strong>Importante:</strong> Honorários devem ser combinados livremente pelo chat. A taxa de conexão do app já foi processada.
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === "client" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-2 ${
                msg.sender === "client"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-foreground"
              }`}
            >
              <p className="text-sm">{msg.text}</p>
              <p
                className={`text-xs mt-1 ${
                  msg.sender === "client" ? "text-primary-foreground/70" : "text-muted-foreground"
                }`}
              >
                {msg.time}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="border-t border-border bg-card p-3">
        <div className="flex gap-2 mb-3">
          <Button variant="outline" size="sm" className="flex-1">
            <Video className="h-4 w-4" />
            Videochamada
          </Button>
          <Button variant="outline" size="sm" className="flex-1">
            <MapPin className="h-4 w-4" />
            Enviar Localização
          </Button>
        </div>

        {/* Message Input */}
        <div className="flex gap-2">
          <Input
            placeholder="Digite sua mensagem..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
          />
          <Button size="icon" onClick={handleSend}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Connection;
