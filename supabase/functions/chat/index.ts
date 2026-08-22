// Edge Function: chat
// Chatbot jurídico do JusCall especializado em:
//  1. Visto para Portugal
//  2. Juros abusivos (revisão de contratos bancários)
//  3. Financiamento de veículo / busca e apreensão
//
// Usa o AI Gateway nativo do Lovable Cloud (LOVABLE_API_KEY).
// Respostas em streaming (SSE).

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const SYSTEM_PROMPT = `Você é a "Ju", assistente virtual do escritório JusCall, um escritório de advocacia brasileiro. Você conversa em português do Brasil, de forma acolhedora, clara e objetiva, com clientes e potenciais clientes.

## Suas áreas de atuação (foque SOMENTE nestes três temas):

1. **Visto para Portugal** — vistos de residência (D7, procura de trabalho, estudante, nômade digital/D8), reagrupamento familiar, cidadania portuguesa, nacionalidade, autorização de residência (AR), CPLP, documentação necessária e prazos.

2. **Juros abusivos** — revisão de contratos bancários e de financiamento, cobrança de juros acima da média de mercado, capitalização indevida, tarifas abusivas, superendividamento, repetição de indébito e renegociação de dívidas.

3. **Financiamento de veículo e busca e apreensão** — atraso de parcelas, ação de busca e apreensão (Decreto-Lei 911/69), purgação da mora, defesa do consumidor, restituição de valores pagos, venda extrajudicial do veículo e negociação com a financeira.

## Como agir:

- Cumprimente e pergunte, de forma gentil, em qual dos três temas você pode ajudar.
- Faça UMA pergunta de cada vez para entender o caso (ex.: valor da dívida, se o veículo já foi apreendido, qual tipo de visto pretende, há quanto tempo etc.).
- Dê orientações jurídicas GERAIS e educativas, em linguagem simples. Explique direitos e possíveis caminhos.
- Sempre que o caso exigir análise, colete os dados de contato do cliente (nome completo, telefone/WhatsApp e melhor horário) e diga que um advogado do JusCall entrará em contato.
- Se o assunto fugir das três áreas, explique com educação que o escritório atende principalmente esses temas e ofereça o contato para os demais casos.

## Regras importantes:

- Você NÃO substitui uma consulta com um advogado. Deixe isso claro quando for dar orientações.
- Nunca garanta resultados de processos ("vai ganhar", "com certeza").
- Não invente leis, valores, prazos ou números de processo. Se não souber, diga que o advogado confirmará.
- Não peça dados sensíveis desnecessários (CPF completo, senhas, número de cartão).
- Seja breve: respostas curtas, com no máximo 2 a 4 parágrafos ou uma lista objetiva.
- Use um tom humano e empático — muitos clientes chegam preocupados.`;

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    if (!LOVABLE_API_KEY) {
      return new Response(
        JSON.stringify({ error: "LOVABLE_API_KEY não configurada." }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const { messages } = await req.json();
    if (!Array.isArray(messages)) {
      return new Response(
        JSON.stringify({ error: "Formato inválido: 'messages' é obrigatório." }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-flash",
        stream: true,
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          ...messages,
        ],
      }),
    });

    if (response.status === 429) {
      return new Response(
        JSON.stringify({ error: "Muitas solicitações. Aguarde um momento e tente novamente." }),
        { status: 429, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }
    if (response.status === 402) {
      return new Response(
        JSON.stringify({ error: "Créditos de IA esgotados. Adicione créditos no Lovable AI." }),
        { status: 402, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }
    if (!response.ok) {
      const errText = await response.text();
      console.error("AI gateway error:", response.status, errText);
      return new Response(
        JSON.stringify({ error: "Erro ao contatar o serviço de IA." }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    // Repassa o streaming (SSE) diretamente para o cliente.
    return new Response(response.body, {
      headers: {
        ...corsHeaders,
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (err) {
    console.error("chat function error:", err);
    return new Response(
      JSON.stringify({ error: "Erro interno no servidor." }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }
});
