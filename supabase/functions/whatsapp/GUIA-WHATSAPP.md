# Guia — IA no WhatsApp da TMS Advogados (100% grátis)

Este guia liga a IA (Groq) ao seu WhatsApp usando a **Meta Cloud API**.
Tudo aqui é **gratuito** e **sem instalar programa** — é só configuração na web.

> Tempo estimado: 30–40 min, uma única vez.

---

## Visão geral do fluxo

```
Cliente no WhatsApp
      │
      ▼
Meta WhatsApp Cloud API  (conexão oficial, grátis)
      │  (webhook)
      ▼
Edge Function "whatsapp"  (roda no seu Supabase / Lovable Cloud, grátis)
      │
      ▼
Groq  (IA gratuita, modelos Llama) ──► resposta volta pelo WhatsApp
```

---

## Passo 1 — Criar a chave gratuita da Groq (a IA)

1. Acesse **https://console.groq.com** e crie a conta (grátis, sem cartão).
2. Menu **API Keys → Create API Key**.
3. Copie a chave (começa com `gsk_...`). Guarde — é o valor de `GROQ_API_KEY`.

---

## Passo 2 — Criar o app no Meta for Developers

1. Acesse **https://developers.facebook.com** e faça login com sua conta do Facebook.
2. **My Apps → Create App → tipo "Business"**.
3. No painel do app, adicione o produto **WhatsApp** (botão *Set up*).
4. Em **WhatsApp → API Setup** você verá:
   - Um **número de teste** grátis (dá para começar já).
   - O **Phone number ID** → é o valor de `WHATSAPP_PHONE_NUMBER_ID`.
   - Um **token temporário** (24h) para testes.
5. Adicione o **seu celular** em *"To"* para receber as mensagens de teste.

> Para produção (seu número real +55 11 99153-7423), você adiciona o número em
> **WhatsApp → Phone numbers** e conclui a verificação. O número precisa **não
> estar** ativo no app WhatsApp comum/Business ao ser migrado para a API.

---

## Passo 3 — Token permanente (para não expirar em 24h)

1. Vá em **https://business.facebook.com → Configurações do Negócio → Usuários → Usuários do sistema**.
2. Crie um **System User** (função Admin).
3. **Add Assets** → selecione seu app do WhatsApp com permissão total.
4. **Generate token** → marque as permissões `whatsapp_business_messaging` e
   `whatsapp_business_management` → gere e **copie o token**.
   Esse é o `WHATSAPP_TOKEN` (permanente).

---

## Passo 4 — Definir os segredos (Secrets)

No painel do **Lovable Cloud / Supabase** do projeto, em
**Edge Functions → Secrets** (ou *Project Settings → Functions → Secrets*),
crie:

| Nome | Valor |
|------|-------|
| `GROQ_API_KEY` | a chave `gsk_...` do Passo 1 |
| `WHATSAPP_TOKEN` | o token permanente do Passo 3 |
| `WHATSAPP_PHONE_NUMBER_ID` | o Phone number ID do Passo 2 |
| `WHATSAPP_VERIFY_TOKEN` | uma **palavra secreta que você inventa** (ex.: `tms-adv-2026`) |

> `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` já existem automaticamente — não precisa criar.

---

## Passo 5 — Publicar a função e pegar a URL

A função `whatsapp` é publicada automaticamente pelo Lovable Cloud ao sincronizar o projeto.
A URL dela fica assim:

```
https://lyjuviasrlmlrijknxbv.supabase.co/functions/v1/whatsapp
```

---

## Passo 6 — Conectar o webhook na Meta

1. No painel do app: **WhatsApp → Configuration → Webhook → Edit**.
2. **Callback URL:** a URL do Passo 5.
3. **Verify token:** exatamente o mesmo valor que você pôs em `WHATSAPP_VERIFY_TOKEN`.
4. Clique **Verify and save** (a Meta faz um GET de verificação — a função responde sozinha).
5. Em **Webhook fields**, clique **Manage** e assine o campo **`messages`**.

---

## Passo 7 — Testar 🎉

- Mande uma mensagem do seu celular para o número (de teste ou o oficial).
- A "Ju" deve responder em alguns segundos, com IA, sobre vistos, juros abusivos
  ou busca e apreensão.

---

## Custos (para deixar claro)

- **Groq:** plano gratuito (limite generoso de mensagens/dia).
- **Meta Cloud API:** as **conversas iniciadas pelo cliente** têm um volume
  mensal gratuito; acima disso a Meta cobra por conversa (centavos). Para um
  escritório começando, normalmente fica no gratuito.
- **Supabase/Lovable Cloud:** execução da função no plano gratuito.

Nenhuma instalação de programa é necessária — tudo é configuração pela web.

---

## Dúvidas comuns

- **"Verify and save" falhou:** confira se `WHATSAPP_VERIFY_TOKEN` é idêntico
  nos dois lados e se a função já está publicada.
- **Não recebo resposta:** veja os **Logs** da Edge Function `whatsapp` no
  Supabase; geralmente é `WHATSAPP_TOKEN` expirado (use o permanente do Passo 3)
  ou o campo `messages` não assinado no Passo 6.
- **A IA não lembra do que foi dito:** confirme que a migração
  `wa_conversations` foi aplicada (tabela criada).
