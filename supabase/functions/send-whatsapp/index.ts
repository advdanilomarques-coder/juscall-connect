// Supabase Edge Function: send-whatsapp
// Envia uma mensagem de texto pela WhatsApp Cloud API (Meta).
//
// Os segredos ficam SOMENTE no servidor (nunca no frontend):
//   WHATSAPP_ACCESS_TOKEN    -> Token de acesso da Meta
//   WHATSAPP_PHONE_NUMBER_ID -> ID do número de telefone (WhatsApp > API Setup)
//
// Chamada a partir do frontend:
//   supabase.functions.invoke("send-whatsapp", { body: { to, text } })

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const GRAPH_VERSION = "v21.0";

Deno.serve(async (req) => {
  // Preflight CORS
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return json({ error: "Método não permitido" }, 405);
  }

  const accessToken = Deno.env.get("WHATSAPP_ACCESS_TOKEN");
  const phoneNumberId = Deno.env.get("WHATSAPP_PHONE_NUMBER_ID");

  if (!accessToken || !phoneNumberId) {
    return json(
      {
        error:
          "Credenciais ausentes. Configure WHATSAPP_ACCESS_TOKEN e WHATSAPP_PHONE_NUMBER_ID nos secrets do Supabase.",
      },
      500,
    );
  }

  let body: { to?: string; text?: string };
  try {
    body = await req.json();
  } catch {
    return json({ error: "Corpo da requisição inválido (JSON esperado)." }, 400);
  }

  const to = (body.to ?? "").replace(/\D/g, ""); // só dígitos: ex. 5511999998888
  const text = (body.text ?? "").trim();

  if (!to || !text) {
    return json(
      { error: 'Campos obrigatórios: "to" (número com DDI) e "text".' },
      400,
    );
  }

  const url = `https://graph.facebook.com/${GRAPH_VERSION}/${phoneNumberId}/messages`;

  const resp = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      messaging_product: "whatsapp",
      recipient_type: "individual",
      to,
      type: "text",
      text: { preview_url: false, body: text },
    }),
  });

  const data = await resp.json();

  if (!resp.ok) {
    // A Meta devolve detalhes úteis em data.error (ex.: token expirado, número não autorizado)
    return json({ error: "Falha ao enviar mensagem", details: data }, resp.status);
  }

  return json({ success: true, data }, 200);
});

function json(payload: unknown, status: number) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}
