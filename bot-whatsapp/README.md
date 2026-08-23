# 🤖 Robô de WhatsApp — TMS Advogados Associados

Robô que roda **no seu computador** (VS Code), mostra o **QR Code do WhatsApp**,
fica **logado** e **responde os clientes automaticamente** sobre vistos para
Portugal, juros abusivos e busca e apreensão de veículo.

**100% gratuito. Não usa nenhuma API paga.**

---

## ✅ O que você precisa antes

1. **Node.js 18 ou superior** instalado → baixe em https://nodejs.org (versão LTS).
2. **VS Code** (ou qualquer terminal).
3. Seu **celular com WhatsApp** (comum ou Business) para escanear o QR.

Para conferir se o Node está instalado, abra o terminal e digite:

```bash
node -v
```

Se aparecer um número (ex.: `v20.11.0`), está tudo certo.

---

## ▶️ Como rodar (passo a passo)

1. Abra a pasta **`bot-whatsapp`** no VS Code
   (menu **Arquivo → Abrir Pasta...**).

2. Abra o terminal integrado: menu **Terminal → Novo Terminal**.

3. Instale as dependências (só na primeira vez):

   ```bash
   npm install
   ```

   > Isso baixa a biblioteca do WhatsApp e um navegador interno. Pode levar alguns minutos.

4. Inicie o robô:

   ```bash
   npm start
   ```

5. Vai aparecer um **QR Code no terminal** (e também salvo em `qrcode-conexao.png`).
   No celular, abra:

   **WhatsApp → Configurações → Aparelhos conectados → Conectar um aparelho**

   e **escaneie o QR** que apareceu no terminal.

6. Quando aparecer `✅ Robô conectado e atendendo!`, está funcionando. 🎉
   Mande uma mensagem de outro número para testar.

> **Deixe a janela/terminal aberta** enquanto quiser que o robô atenda.
> Para parar, pressione **Ctrl + C**.

---

## 🔒 Fica logado

Depois do primeiro QR, a sessão fica salva na pasta `.wwebjs_auth`.
Nas próximas vezes é só rodar `npm start` — **não precisa escanear de novo**.

Para desconectar de verdade: no celular, em *Aparelhos conectados*, remova o
aparelho; ou apague a pasta `.wwebjs_auth` e rode de novo.

---

## ✏️ Como mudar as respostas

Abra o arquivo **`index.js`**. No topo estão:

- `NOME_ESCRITORIO`, `HORARIO` — dados do escritório.
- O objeto **`RESP`** — todos os textos das respostas (visto, juros, carro, doc, valores).
- `MENU` — o menu inicial.

Edite o texto entre aspas, salve e rode `npm start` de novo.

---

## ⚠️ Avisos importantes

- Este robô usa a tecnologia do **WhatsApp Web** (não oficial). Funciona muito
  bem para um escritório, mas **o computador precisa ficar ligado** com o robô
  rodando para atender.
- Use com bom senso e de acordo com as regras do WhatsApp (não enviar spam).
- As respostas são **orientações gerais** e não substituem a análise de um advogado
  (isso já vai escrito no rodapé de cada mensagem).

---

## 🆙 Quiser evoluir depois

- Ligar uma **IA de verdade** (Groq/Gemini) para respostas mais naturais.
- Registrar os **leads** (nome, telefone, caso) numa planilha ou banco.
- Enviar um **aviso para você** quando chegar cliente novo.

É só chamar que a gente monta. 🙂
