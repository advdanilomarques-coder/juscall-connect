// Edge Function: whatsapp
// Atendimento com IA da TMS Advogados Associados DIRETO no WhatsApp.
//
// Fluxo (100% gratuito):
//   Cliente -> WhatsApp -> Meta Cloud API (webhook) -> ESTA função -> Groq (IA) -> resposta no WhatsApp
//
// Provedores usados (todos com plano gratuito):
//   - Meta WhatsApp Cloud API  (conexão oficial e gratuita com o WhatsApp)
//   - Groq                     (IA gratuita, modelos Llama)
//   - Supabase Edge Functions  (execução gratuita, já incluída no Lovable Cloud)
//
// Segredos necessários (configurar no painel de Secrets):
//   WHATSAPP_VERIFY_TOKEN     -> palavra secreta que VOCÊ inventa (usada na verificação do webhook)
//   WHATSAPP_TOKEN            -> token de acesso da Meta (permanente / system user)
//   WHATSAPP_PHONE_NUMBER_ID  -> ID do número (aparece no painel da Meta)
//   GROQ_API_KEY              -> chave gratuita criada em console.groq.com
//   (opcionais)
//   WHATSAPP_APP_SECRET       -> App Secret da Meta, para validar a assinatura dos webhooks
//   SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY -> já existem no ambiente; usados p/ memória da conversa

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const GRAPH_VERSION = "v21.0";
const GROQ_MODEL = "llama-3.3-70b-versatile";
const HISTORY_LIMIT = 12; // nº de mensagens mantidas por cliente
const HISTORY_TTL_MIN = 60; // esquece a conversa após X minutos de inatividade

const SYSTEM_PROMPT = `Você é a "Ju", assistente virtual do escritório TMS Advogados Associados, um escritório de advocacia brasileiro. Você conversa por WhatsApp, em português do Brasil, de forma acolhedora, humana e objetiva.

## Áreas de atuação (foque SOMENTE nestes três temas):
1. **Visto para Portugal** — vistos de residência (D7, procura de trabalho, estudante/D4, D8), reagrupamento familiar, nacionalidade, CPLP, documentos e prazos.
2. **Juros abusivos** — revisão de contratos bancários e de financiamento, capitalização indevida, tarifas e seguros abusivos, superendividamento, recuperação de valores.
3. **Financiamento de veículo e busca e apreensão** — atraso de parcelas, ação de busca e apreensão (DL 911/69), purgação da mora, defesa do consumidor, negociação com a financeira.

## Como agir:
- Cumprimente e pergunte, com gentileza, em qual dos três temas pode ajudar.
- Faça UMA pergunta por vez para entender o caso.
- Dê orientações jurídicas GERAIS e educativas, em linguagem simples.
- Quando fizer sentido, informe os documentos necessários daquele caso.
- Sobre valores: diga que a PRIMEIRA conversa é gratuita e que os honorários são definidos APÓS a análise do caso (justo e transparente, sem tabela fixa). Nunca invente valores.
- Colete nome completo e resuma o caso, e diga que um advogado do escritório dará continuidade ao atendimento.

## Regras:
- Você NÃO substitui a consulta com um advogado — deixe isso claro ao orientar.
- Nunca garanta resultados ("vai ganhar", "com certeza").
- Não invente leis, prazos, valores ou números de processo.
- Não peça dados sensíveis desnecessários (CPF completo, senhas, cartão).
- Mensagens CURTAS (é WhatsApp): no máximo 2 parágrafos curtos ou uma lista objetiva. Pode usar emojis com moderação.
- Se o assunto fugir das três áreas, explique com educação e ofereça encaminhar ao escritório.`;

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

function supa() {
  const url = Deno.env.get("SUPABASE_URL");
  const key = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !key) return null;
  return createClient(url, key, { auth: { persistSession: false } });
}

// ---- memória da conversa (opcional; requer a tabela wa_conversations) ----
async function loadHistory(phone: string): Promise<{ role: string; content: string }[]> {
  const db = supa();
  if (!db) return [];
  try {
    const { data } = await db
      .from("wa_conversations")
      .select("history, updated_at")
      .eq("phone", phone)
      .maybeSingle();
    if (!data) return [];
    const ageMin = (Date.now() - new Date(data.updated_at).getTime()) / 60000;
    if (ageMin > HISTORY_TTL_MIN) return [];
    return Array.isArray(data.history) ? data.history : [];
  } catch (_e) {
    return [];
  }
}

async function saveHistory(phone: string, history: { role: string; content: string }[]) {
  const db = supa();
  if (!db) return;
  try {
    const trimmed = history.slice(-HISTORY_LIMIT);
    await db
      .from("wa_conversations")
      .upsert({ phone, history: trimmed, updated_at: new Date().toISOString() }, { onConflict: "phone" });
  } catch (_e) {
    // memória é opcional — segue sem ela
  }
}

// ---- IA (Groq) ----
async function askGroq(messages: { role: string; content: string }[]): Promise<string> {
  const key = Deno.env.get("GROQ_API_KEY");
  if (!key) return "Nosso atendimento automático está em configuração. Por favor, escreva sua dúvida que um advogado responderá em breve. 🙏";

  const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: GROQ_MODEL,
      temperature: 0.4,
      max_tokens: 500,
      messages: [{ role: "system", content: SYSTEM_PROMPT }, ...messages],
    }),
  });

  if (!res.ok) {
    console.error("Groq error", res.status, await res.text());
    return "Tive uma instabilidade agora. Pode repetir sua última mensagem, por favor? 🙏";
  }
  const json = await res.json();
  return json.choices?.[0]?.message?.content?.trim() ||
    "Desculpe, não entendi. Pode reescrever com mais detalhes?";
}

// ---- envio de resposta pelo WhatsApp (Meta Cloud API) ----
async function sendWhatsApp(to: string, text: string) {
  const token = Deno.env.get("WHATSAPP_TOKEN");
  const phoneId = Deno.env.get("WHATSAPP_PHONE_NUMBER_ID");
  if (!token || !phoneId) {
    console.error("Faltam WHATSAPP_TOKEN / WHATSAPP_PHONE_NUMBER_ID");
    return;
  }
  const res = await fetch(`https://graph.facebook.com/${GRAPH_VERSION}/${phoneId}/messages`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      messaging_product: "whatsapp",
      to,
      type: "text",
      text: { body: text.slice(0, 4000) },
    }),
  });
  if (!res.ok) console.error("WhatsApp send error", res.status, await res.text());
}

Deno.serve(async (req) => {
  const url = new URL(req.url);

  if (req.method === "OPTIONS") return new Response(null, { headers: cors });

  // 1) Verificação do webhook (a Meta chama uma vez, com GET)
  if (req.method === "GET") {
    const mode = url.searchParams.get("hub.mode");
    const token = url.searchParams.get("hub.verify_token");
    const challenge = url.searchParams.get("hub.challenge");
    const verify = Deno.env.get("WHATSAPP_VERIFY_TOKEN");
    if (mode === "subscribe" && token && token === verify) {
      return new Response(challenge ?? "", { status: 200 });
    }
    return new Response("Forbidden", { status: 403 });
  }

  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });

  try {
    const body = await req.json();

    // Estrutura: entry[].changes[].value.messages[]
    const value = body?.entry?.[0]?.changes?.[0]?.value;
    const msg = value?.messages?.[0];

    // Ignora eventos que não são mensagem de texto recebida (status, reações, etc.)
    if (!msg || msg.type !== "text") {
      return new Response("ok", { status: 200, headers: cors });
    }

    const from: string = msg.from; // número do cliente (ex.: 5511999999999)
    const userText: string = msg.text?.body ?? "";
    if (!userText.trim()) return new Response("ok", { status: 200, headers: cors });

    // Responde de forma assíncrona para devolver 200 rápido à Meta
    const work = (async () => {
      const history = await loadHistory(from);
      history.push({ role: "user", content: userText });
      const reply = await askGroq(history);
      history.push({ role: "assistant", content: reply });
      await saveHistory(from, history);
      await sendWhatsApp(from, reply);
    })();

    // @ts-ignore EdgeRuntime existe no ambiente Supabase
    if (typeof EdgeRuntime !== "undefined") EdgeRuntime.waitUntil(work);
    else await work;

    return new Response("ok", { status: 200, headers: cors });
  } catch (err) {
    console.error("whatsapp function error", err);
    return new Response("ok", { status: 200, headers: cors }); // 200 evita reentrega em loop
  }
});
