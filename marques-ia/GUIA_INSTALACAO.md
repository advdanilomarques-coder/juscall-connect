# Marques IA — Guia Completo, Comando por Comando

Este guia leva você do zero até o WhatsApp respondendo de verdade, com cada
comando de terminal explicado individualmente. Nenhum cartão de crédito é
necessário em nenhuma etapa.

---

## Parte 1 — Como pegar a chave de API gratuita (OpenRouter)

1. Acesse **https://openrouter.ai** no navegador.
2. Clique em **"Sign In"** (canto superior direito) e crie uma conta — Google,
   GitHub ou e-mail. Gratuito, sem cartão.
3. Acesse **https://openrouter.ai/keys** (ou avatar → **"Keys"**).
4. Clique em **"Create Key"**, dê um nome (ex.: `marques-ia`) e confirme.
5. Copie a chave exibida (formato `sk-or-v1-...`) — ela só aparece uma vez.
   Guarde em local seguro.

---

## Parte 2 — Instalação do backend, comando por comando

**Pré-requisitos:** Python 3.11+, Docker Desktop instalado e **aberto**.

### Comando 1 — Verificar se o Python está instalado

```bash
python3 --version
```
Deve mostrar `Python 3.11` ou superior. Se não tiver, instale antes de continuar.

### Comando 2 — Verificar se o Docker está instalado e rodando

```bash
docker --version
```
Se der erro, abra o aplicativo Docker Desktop manualmente e espere ele ficar
"Running" antes de seguir.

### Comando 3 — Extrair o projeto baixado

```bash
unzip marques-ia-backend-ia.zip
```

### Comando 4 — Entrar na pasta do projeto

```bash
cd marques-ia
```

### Comando 5 — Conferir os arquivos (opcional, só para checar)

```bash
ls -la
```
Você deve ver `install-all.sh`, `.env.example`, as pastas `backend/` e `docker/`.

### Comando 6 — Criar o arquivo de configuração real

```bash
cp .env.example .env
```

### Comando 7 — Colar sua chave da OpenRouter no .env

No macOS (sed do BSD, repare o `''` depois de `-i`):
```bash
sed -i '' "s/coloque_aqui_sua_unica_chave_gratuita/SUA_CHAVE_AQUI/" .env
```
No Linux:
```bash
sed -i "s/coloque_aqui_sua_unica_chave_gratuita/SUA_CHAVE_AQUI/" .env
```
Troque `SUA_CHAVE_AQUI` pela chave copiada na Parte 1.

### Comando 8 — Gerar uma chave secreta segura para o JWT

macOS:
```bash
sed -i '' "s/troque_por_uma_chave_secreta_aleatoria_bem_longa/$(openssl rand -hex 32)/" .env
```
Linux:
```bash
sed -i "s/troque_por_uma_chave_secreta_aleatoria_bem_longa/$(openssl rand -hex 32)/" .env
```

### Comando 9 — Definir a senha do administrador do painel

macOS:
```bash
sed -i '' "s/troque_esta_senha_admin/MinhaSenh@Segura123/" .env
```
Linux:
```bash
sed -i "s/troque_esta_senha_admin/MinhaSenh@Segura123/" .env
```
Troque `MinhaSenh@Segura123` pela senha que você quiser usar para logar no painel.

### Comando 10 — Dar permissão de execução ao instalador

```bash
chmod +x install-all.sh
```

### Comando 11 — Rodar a instalação completa

```bash
./install-all.sh
```
Esse único comando faz tudo: cria o ambiente virtual, instala as dependências,
sobe o Postgres e o Redis via Docker, cria o administrador, valida sua chave
da OpenRouter e inicia a aplicação em `http://localhost:8000`.

Deixe este terminal aberto — é ele quem está rodando o servidor. Abra um
**novo terminal** para os próximos comandos.

---

## Parte 3 — Testar o backend (novo terminal)

### Comando 12 — Verificar se a API está no ar

```bash
curl http://localhost:8000
```

### Comando 13 — Fazer login e pegar o token

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@marquesadvogados.com.br&password=MinhaSenh@Segura123"
```
Copie o valor de `access_token` da resposta.

### Comando 14 — Testar o agente de IA (cliente novo)

```bash
curl -X POST http://localhost:8000/chat/testar \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
        "telefone": "5511991537423",
        "mensagem": "Bom dia, gostaria de entender sobre revisão de contrato bancário",
        "nome_cliente": "Maria Souza"
      }'
```
A resposta traz `"cliente_novo": true`. Repita o comando com o **mesmo
telefone** e uma nova mensagem: a resposta virá com `"cliente_novo": false`,
confirmando que o agente reconheceu o cliente como recorrente.

---

## Parte 4 — Conectar o WhatsApp de verdade (webhook)

O backend já expõe o endpoint `/webhook/whatsapp` (verificação + recebimento
de mensagens). Para a Meta conseguir chamá-lo, seu `localhost:8000` precisa
de uma URL pública HTTPS — usamos o **ngrok** (gratuito) para isso.

### Comando 15 — Instalar o ngrok (macOS via Homebrew)

```bash
brew install ngrok
```

### Comando 16 — Criar conta gratuita e configurar o token do ngrok

1. Crie uma conta grátis em **https://dashboard.ngrok.com/signup**.
2. Copie seu authtoken em **https://dashboard.ngrok.com/get-started/your-authtoken**.
3. Configure localmente:
```bash
ngrok config add-authtoken SEU_TOKEN_DO_NGROK
```

### Comando 17 — Expor o servidor local publicamente

Em um terceiro terminal (deixe o `install-all.sh` rodando no primeiro):
```bash
ngrok http 8000
```
O ngrok vai mostrar uma URL do tipo `https://xxxx-xx-xx.ngrok-free.app`.
Copie essa URL.

### Passo 18 — Configurar o webhook no Meta for Developers

1. Acesse **https://developers.facebook.com/apps** e entre no app do WhatsApp
   Business já criado para o número `+55 11 99153-7423`.
2. Vá em **WhatsApp → Configuração (Configuration)**.
3. Em **Webhook**, clique em **"Edit"** e preencha:
   - **Callback URL:** `https://xxxx-xx-xx.ngrok-free.app/webhook/whatsapp`
     (a URL do ngrok do comando 17, com `/webhook/whatsapp` no final)
   - **Verify Token:** o mesmo valor definido em `WHATSAPP_VERIFY_TOKEN` no
     seu `.env`
4. Clique em **"Verify and Save"** — se aparecer erro, confira se o
   `install-all.sh` (comando 11) ainda está rodando.
5. Em **"Webhook fields"**, clique em **"Manage"** e assine o campo
   **`messages`**.
6. Em **Configurações → Básico** do app, copie o **App Secret** e cole na
   variável `WHATSAPP_APP_SECRET` do `.env`. Isso ativa a validação de
   assinatura (`X-Hub-Signature-256`) das mensagens recebidas — sem isso,
   qualquer pessoa que descobrir sua URL do ngrok poderia enviar mensagens
   falsas para o webhook. Reinicie o `install-all.sh` depois de preencher.

### Comando 19 — Testar de verdade

Mande uma mensagem pelo WhatsApp para `+55 11 99153-7423`. Ela deve chegar
ao backend, o agente processa (reconhecendo se é cliente novo ou antigo) e a
resposta volta automaticamente para o WhatsApp do cliente.

> Nota: a URL do ngrok gratuito muda a cada reinício. Ao reiniciar o ngrok,
> repita o Passo 18 com a nova URL.

---

## Parte 5 — Testar o CRM e a geração de contratos

Use o mesmo token do Comando 13.

### Comando 20 — Listar clientes cadastrados

```bash
curl http://localhost:8000/crm/clientes \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Comando 21 — Ver o kanban (casos agrupados por etapa do funil)

```bash
curl http://localhost:8000/crm/kanban \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```
Todo cliente novo que fala com o agente (Parte 3 ou Parte 4) já entra
automaticamente na etapa `novo_lead`.

### Comando 22 — Mover um caso no funil (ex.: para "qualificacao")

```bash
curl -X PATCH http://localhost:8000/crm/casos/1 \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"etapa_funil": "qualificacao", "resumo": "Cliente quer revisar juros do financiamento"}'
```

### Comando 23 — Gerar um contrato em PDF para o caso

```bash
curl -X POST http://localhost:8000/contratos/gerar \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"caso_id": 1, "tipo": "acao_revisional"}'
```
Tipos disponíveis: `acao_revisional`, `busca_e_apreensao`, `honorarios`.
O contrato nasce em status `rascunho` e o caso avança automaticamente para a
etapa `contrato` no kanban.

### Comando 24 — Aprovar o contrato (obrigatório antes de enviar ao cliente)

```bash
curl -X PATCH http://localhost:8000/contratos/1/aprovar \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Comando 25 — Baixar o PDF do contrato

```bash
curl http://localhost:8000/contratos/1/download \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -o contrato_1.pdf
```

---

## Parte 6 — Painel Visual, Testes Automatizados e Backup

### Painel administrativo (navegador)

Com o `install-all.sh` rodando, acesse no navegador:

```
http://localhost:8000/painel
```

Faça login com o e-mail/senha definidos no `.env`. O painel mostra o kanban
de casos, a lista de clientes (com busca) e o log de auditoria — tudo
puxando dos mesmos endpoints usados nos comandos `curl` acima.

### Rodar os testes automatizados

Em um terminal novo, na raiz do projeto:

```bash
chmod +x test.sh
./test.sh
```

Isso instala o `pytest` no mesmo ambiente virtual e roda os testes que
cobrem o failover de IA, o reconhecimento de cliente novo/antigo e a
validação de assinatura do webhook.

### Gerar um backup

```bash
chmod +x backup.sh
./backup.sh
```

Gera um dump do PostgreSQL e uma cópia dos contratos em PDF dentro de
`backups/AAAAMMDD_HHMMSS/`.

---

## Parte 7 — OCR, Base de Conhecimento (RAG) e Automação (n8n)

### Pré-requisito do OCR: instalar o Tesseract

```bash
# macOS:
brew install tesseract tesseract-lang

# Linux:
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

### Comando 29 — Enviar um documento para OCR

```bash
curl -X POST http://localhost:8000/documentos/upload \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -F "caso_id=1" \
  -F "arquivo=@/caminho/para/documento.pdf"
```
A resposta traz um preview do texto extraído e `confianca_ocr`. Se a
confiança for baixa, `revisao_manual_recomendada` vem `true`.

### Comando 30 — Popular a base de conhecimento (RAG) manualmente

O `install-all.sh` já roda isso automaticamente na instalação, mas você pode
adicionar novos trechos a qualquer momento:

```bash
curl -X POST http://localhost:8000/rag/documentos \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"area_juridica": "direito_bancario", "titulo": "Tarifas bancárias indevidas", "conteudo": "..."}'
```

### Comando 31 — Testar a busca do RAG manualmente

```bash
curl "http://localhost:8000/rag/buscar?q=juros%20abusivos%20financiamento" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```
O agente já usa essa mesma busca automaticamente antes de responder qualquer
cliente — o resultado aqui é só para conferir o que está sendo usado.

### Importar os workflows do n8n

A pasta `n8n/workflows/` traz 4 arquivos prontos para importar (n8n → menu
"..." → Import from File):

- `lembrete_followup.json` — sinaliza casos parados há mais de 3 dias.
- `notificacao_novo_caso.json` — avisa a equipe por e-mail a cada novo lead.
- `backup_periodico.json` — roda o `backup.sh` todo dia às 3h.
- `healthcheck_ia.json` — alerta por e-mail se todos os modelos gratuitos falharem.

Cada workflow precisa de duas credenciais configuradas no n8n antes de ativar:
- **HTTP Header Auth** chamada "Marques IA - Token Admin", com o header
  `Authorization: Bearer SEU_TOKEN_AQUI`.
- **SMTP** chamada "SMTP do Escritório", para os workflows que enviam e-mail.

---

## Bloco único da Parte 2 (tudo em sequência)

Se preferir colar tudo de uma vez, substitua `SUA_CHAVE_AQUI` e rode:

```bash
unzip marques-ia-backend-ia.zip && cd marques-ia && \
cp .env.example .env && \
sed -i '' "s/coloque_aqui_sua_unica_chave_gratuita/SUA_CHAVE_AQUI/" .env && \
sed -i '' "s/troque_por_uma_chave_secreta_aleatoria_bem_longa/$(openssl rand -hex 32)/" .env && \
sed -i '' "s/troque_esta_senha_admin/MinhaSenh@Segura123/" .env && \
chmod +x install-all.sh && \
./install-all.sh
```
> No Linux, troque `sed -i ''` por `sed -i` (sem o `''`) nas três linhas.

---

## Parte 8 — Enviar contratos por e-mail para o cliente (novo)

O backend agora envia o contrato aprovado, em PDF, direto para o e-mail do
cliente. É **opcional**: se você não configurar o SMTP, todo o resto continua
funcionando normalmente.

### Passo 32 — Configurar o SMTP no `.env`

Preencha no `.env` (exemplo para Gmail):

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seuemail@gmail.com
SMTP_PASSWORD=senha_de_app_do_gmail
SMTP_FROM_EMAIL=seuemail@gmail.com
SMTP_FROM_NAME=Marques Advogados Associados
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

> No Gmail, **não use sua senha normal**: gere uma "Senha de app" em
> https://myaccount.google.com/apppasswords e cole em `SMTP_PASSWORD`.
> Depois de preencher, reinicie o `install-all.sh`.

### Passo 33 — Cadastrar o e-mail do cliente

Pelo painel (`/painel` → aba **Clientes** → **Editar**) ou via API:

```bash
curl -X PATCH http://localhost:8000/crm/clientes/1 \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"email": "cliente@exemplo.com"}'
```

### Passo 34 — Aprovar e enviar o contrato

Pelo painel, aba **Contratos**: clique em **Aprovar** e depois em **Enviar
e-mail**. Ou via API:

```bash
# aprovar (obrigatório antes de enviar)
curl -X PATCH http://localhost:8000/contratos/1/aprovar \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# enviar por e-mail (com o PDF em anexo)
curl -X POST http://localhost:8000/contratos/1/enviar \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

Só é possível enviar contratos **aprovados** e para clientes **com e-mail
cadastrado** — uma trava de segurança para nunca enviar rascunho ao cliente.

---

## Parte 9 — Novidades do painel (`/painel`)

O painel administrativo agora tem quatro abas:

- **Kanban** — cada card tem um seletor para **mover o caso** entre as etapas
  do funil direto pela tela.
- **Clientes** — busca + botão **Editar** para ajustar nome e **e-mail** do cliente.
- **Contratos** (nova) — gerar contrato (por nº de caso e tipo), **aprovar**,
  **enviar por e-mail** e **baixar** o PDF.
- **Auditoria** — histórico de ações.
