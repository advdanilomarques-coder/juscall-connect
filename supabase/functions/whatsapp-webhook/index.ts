// Supabase Edge Function: whatsapp-webhook
// Recebe eventos da WhatsApp Cloud API (Meta).
//
//   GET  -> Verificação do webhook (a Meta chama uma vez ao configurar).
//   POST -> Mensagens e status recebidos.
//
// Segredo necessário (server-side):
//   WHATSAPP_VERIFY_TOKEN -> string que VOCÊ inventa e cola nos dois lugares
//                            (aqui como secret e no painel da Meta).
//
// IMPORTANTE: esta função precisa de verify_jwt = false no config.toml,
// porque a Meta chama sem o header de autenticação do Supabase.

Deno.serve(async (req) => {
  const url = new URL(req.url);

  // --- Verificação do webhook (handshake da Meta) ---
  if (req.method === "GET") {
    const mode = url.searchParams.get("hub.mode");
    const token = url.searchParams.get("hub.verify_token");
    const challenge = url.searchParams.get("hub.challenge");

    const verifyToken = Deno.env.get("WHATSAPP_VERIFY_TOKEN");

    if (mode === "subscribe" && token === verifyToken && challenge) {
      // Devolve o challenge em texto puro -> a Meta valida o webhook.
      return new Response(challenge, {
        status: 200,
        headers: { "Content-Type": "text/plain" },
      });
    }

    return new Response("Forbidden", { status: 403 });
  }

  // --- Recebimento de mensagens/status ---
  if (req.method === "POST") {
    try {
      const payload = await req.json();

      // Estrutura: entry[].changes[].value.messages[]
      const entries = payload?.entry ?? [];
      for (const entry of entries) {
        for (const change of entry?.changes ?? []) {
          const value = change?.value ?? {};

          for (const message of value.messages ?? []) {
            const from = message.from; // número de quem enviou (com DDI)
            const type = message.type; // text, image, audio, etc.
            const text = message.text?.body ?? "";
            console.log("Mensagem recebida:", { from, type, text });

            // TODO: aqui você grava a mensagem no banco (tabela do Supabase)
            // para aparecer no chat do Connection.tsx em tempo real.
          }

          for (const status of value.statuses ?? []) {
            // sent / delivered / read / failed
            console.log("Status:", status.id, status.status);
          }
        }
      }
    } catch (err) {
      console.error("Erro ao processar webhook:", err);
    }

    // Sempre responder 200 rápido, senão a Meta reenvia o evento.
    return new Response("EVENT_RECEIVED", { status: 200 });
  }

  return new Response("Method Not Allowed", { status: 405 });
});
