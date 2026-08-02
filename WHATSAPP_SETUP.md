# Integração WhatsApp Cloud API — JusCall Connect

Guia para conectar o app à **WhatsApp Cloud API** da Meta e enviar/receber mensagens reais.

> ⚠️ **Regra de ouro:** o **Access Token NUNCA** vai no frontend (React). Ele fica
> apenas como **secret no Supabase**, usado pelas Edge Functions. Se o token for
> exposto no navegador, qualquer pessoa pode enviar mensagens em seu nome.

---

## 1. As 4 credenciais que você precisa pegar

No painel <https://developers.facebook.com> → seu app → menu **WhatsApp → API Setup (Configuração da API)**:

| Credencial | Onde encontrar | Exemplo |
|---|---|---|
| **App ID** | Topo do painel do app (ou em *Configurações → Básico*) | `1234567890123456` |
| **Phone Number ID** | WhatsApp → API Setup, campo **"Identificação do número de telefone"** | `109876543210987` |
| **Access Token** | WhatsApp → API Setup, botão **"Gerar token de acesso"** | `EAAG...` (string longa) |
| **Verify Token** | **Você inventa** uma senha qualquer (ex.: `juscall_2026_xyz`) | qualquer texto secreto |

### Sobre o Access Token (importante)

- O token que aparece na tela "API Setup" é **temporário (dura 24h)** — bom só para testar.
- Para produção, gere um **token permanente** com um *System User*:
  1. <https://business.facebook.com> → **Configurações do Negócio → Usuários → Usuários do sistema**
  2. Crie um usuário do sistema → **Gerar novo token**
  3. Selecione o app, marque as permissões **`whatsapp_business_messaging`** e **`whatsapp_business_management`**
  4. Copie o token (ele **não expira**).

---

## 2. Onde colar as credenciais (secrets do Supabase)

Essas variáveis ficam no Supabase, **não** no arquivo `.env` do projeto.

**Opção A — Painel:** Supabase → seu projeto → **Edge Functions → Manage secrets** → adicione:

```
WHATSAPP_ACCESS_TOKEN     = EAAG... (seu token)
WHATSAPP_PHONE_NUMBER_ID  = 109876543210987
WHATSAPP_VERIFY_TOKEN     = juscall_2026_xyz   (o que você inventou)
```

**Opção B — CLI:**

```sh
supabase secrets set WHATSAPP_ACCESS_TOKEN="EAAG..."
supabase secrets set WHATSAPP_PHONE_NUMBER_ID="109876543210987"
supabase secrets set WHATSAPP_VERIFY_TOKEN="juscall_2026_xyz"
```

> O **App ID** não precisa ir para os secrets para enviar mensagens — ele serve
> para identificar o app no painel da Meta. Guarde-o para referência.

---

## 3. Publicar (deploy) as Edge Functions

```sh
supabase functions deploy send-whatsapp
supabase functions deploy whatsapp-webhook
```

As funções ficam em:
- `supabase/functions/send-whatsapp/index.ts`  → envia mensagens
- `supabase/functions/whatsapp-webhook/index.ts` → recebe mensagens

---

## 4. Configurar o Webhook na Meta (para RECEBER mensagens)

1. Copie a URL da função webhook:
   ```
   https://lyjuviasrlmlrijknxbv.supabase.co/functions/v1/whatsapp-webhook
   ```
2. Na Meta: **WhatsApp → Configuration → Webhook → Editar**
   - **Callback URL:** cole a URL acima
   - **Verify token:** o mesmo valor de `WHATSAPP_VERIFY_TOKEN`
3. Clique **Verificar e salvar** (a Meta chama o webhook e valida).
4. Em **Webhook fields**, assine o campo **`messages`**.

---

## 5. Enviar mensagem a partir do app (React)

```ts
import { supabase } from "@/integrations/supabase/client";

const { data, error } = await supabase.functions.invoke("send-whatsapp", {
  body: {
    to: "5511999998888",           // número com DDI (55) + DDD, só dígitos
    text: "Olá! Sua conexão foi confirmada no JusCall.",
  },
});
```

> **Teste inicial:** no modo sandbox, a Meta só entrega mensagens para números
> adicionados em **API Setup → "Para" (To)**. Adicione seu próprio WhatsApp lá
> para testar antes de ir para produção.

---

## 6. Checklist rápido

- [ ] App criado em developers.facebook.com com o produto **WhatsApp** adicionado
- [ ] Peguei **Phone Number ID** e **Access Token**
- [ ] Inventei um **Verify Token**
- [ ] Coloquei os 3 secrets no Supabase
- [ ] `supabase functions deploy` das duas funções
- [ ] Webhook configurado e campo `messages` assinado
- [ ] Testei enviando para o meu próprio número
