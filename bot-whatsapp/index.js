/**
 * Robô de atendimento no WhatsApp — TMS Advogados Associados
 * ---------------------------------------------------------------
 * - Roda no seu computador (VS Code / terminal).
 * - Mostra o QR Code do WhatsApp para você escanear em:
 *      WhatsApp -> Configurações -> Aparelhos conectados -> Conectar aparelho
 * - Fica LOGADO (a sessão é salva na pasta .wwebjs_auth, não precisa
 *   escanear de novo toda vez).
 * - Responde os clientes automaticamente sobre:
 *      1) Visto para Portugal
 *      2) Juros abusivos
 *      3) Financiamento / busca e apreensão de veículo
 *
 * 100% gratuito. Não usa nenhuma API paga.
 */

const fs = require("fs");
const path = require("path");
const qrcodeTerminal = require("qrcode-terminal");
const QRCode = require("qrcode");
const { Client, LocalAuth } = require("whatsapp-web.js");

// ------------------------------------------------------------------
// Configurações
// ------------------------------------------------------------------
const NOME_ESCRITORIO = "TMS Advogados Associados";
const HORARIO = "Segunda a sexta, das 9h às 18h";
// Tempo (min) para o robô mostrar o menu de novo para o mesmo cliente.
const REPETIR_SAUDACAO_MIN = 180;

// Guarda a última vez que saudamos cada cliente (memória simples).
const ultimaSaudacao = new Map();

// ------------------------------------------------------------------
// Textos das respostas
// ------------------------------------------------------------------
const MENU =
  `Olá! 👋 Aqui é a *${NOME_ESCRITORIO}*.\n\n` +
  `Sou o atendimento automático e posso te ajudar. Responda com o número:\n\n` +
  `*1* - Visto para Portugal 🇵🇹\n` +
  `*2* - Juros abusivos no contrato 💰\n` +
  `*3* - Financiamento / busca e apreensão do veículo 🚗\n\n` +
  `Digite o número da opção. 😊`;

const RESP = {
  visto:
    `🇵🇹 *VISTO PARA PORTUGAL*\n\n` +
    `Ajudamos brasileiros a morar legalmente em Portugal: D7 (renda própria), ` +
    `procura de trabalho, estudante (D4) e reagrupamento familiar.\n\n` +
    `Me conte seu objetivo (trabalhar, estudar, aposentadoria ou família) que eu já te oriento.\n\n` +
    `Digite *DOC* para ver os documentos ou *VALORES* para saber sobre honorários.`,

  juros:
    `💰 *JUROS ABUSIVOS*\n\n` +
    `Muitos contratos cobram juros acima do permitido, tarifas indevidas e seguros embutidos. ` +
    `Com a revisão, é possível reduzir a parcela e recuperar valores pagos a mais.\n\n` +
    `Me diga qual é o contrato (veículo, empréstimo, cartão ou imóvel).\n\n` +
    `Digite *DOC* para ver os documentos ou *VALORES* para saber sobre honorários.`,

  carro:
    `🚗 *FINANCIAMENTO / BUSCA E APREENSÃO*\n\n` +
    `Fique tranquilo, você tem direitos. Dá para renegociar, fazer a purgação da mora ` +
    `(pagar o atraso e manter o carro) e discutir abusos do contrato.\n\n` +
    `⏱️ O prazo é curto e faz toda a diferença — quanto antes agir, melhor.\n\n` +
    `Me diga sua situação: (a) atrasado nas parcelas, (b) recebi a ação, ou (c) o carro já foi apreendido.\n\n` +
    `Digite *DOC* para ver os documentos ou *VALORES* para saber sobre honorários.`,

  doc:
    `📄 *DOCUMENTOS*\n\n` +
    `• *Visto Portugal:* passaporte válido, comprovação de renda, seguro de saúde, ` +
    `comprovante de moradia e antecedentes criminais.\n` +
    `• *Juros abusivos:* contrato, carnê/parcelas, comprovantes de pagamento e saldo devedor.\n` +
    `• *Veículo:* contrato, documento do carro (CRLV), parcelas pagas e a citação (se houver).\n\n` +
    `Pode enviar por aqui mesmo, em foto ou PDF. 📎`,

  valores:
    `💵 *VALORES*\n\n` +
    `A primeira conversa para entender seu caso é *gratuita e sem compromisso*. 🤝\n\n` +
    `Os honorários são definidos só após a análise, conforme a complexidade — ` +
    `combinados antes de qualquer providência, com transparência e opção de parcelamento.`,

  humano:
    `👩‍⚖️ Certo! Um advogado da *${NOME_ESCRITORIO}* vai assumir a conversa. ` +
    `Nosso horário de atendimento é ${HORARIO}.\n\n` +
    `Enquanto isso, se puder, me adiante seu *nome completo* e um *resumo do caso*. 🙏`,
};

const RODAPE =
  `\n\n_Atendimento automático. As orientações são gerais e não substituem a análise de um advogado._`;

// ------------------------------------------------------------------
// Lógica: decide a resposta a partir da mensagem
// ------------------------------------------------------------------
function normalizar(txt) {
  return (txt || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // remove acentos
    .trim();
}

function definirResposta(texto, chatId) {
  const t = normalizar(texto);

  // Palavras-chave / opções
  if (["1", "um"].includes(t) || /(visto|portugal|imigra|cidadania|nacionalidade)/.test(t)) return RESP.visto;
  if (["2", "dois"].includes(t) || /(juros|abusiv|revis|divida|superendivid)/.test(t)) return RESP.juros;
  if (["3", "tres"].includes(t) || /(carro|veicul|financ|apreens|busca e|parcela)/.test(t)) return RESP.carro;
  if (/(doc|documento)/.test(t)) return RESP.doc;
  if (/(valor|preco|honorar|quanto custa|custa)/.test(t)) return RESP.valores;
  if (/(humano|atendente|advogad|falar com|pessoa)/.test(t)) return RESP.humano;

  // Saudação / mensagem não reconhecida -> mostra o menu (com controle de repetição)
  const agora = Date.now();
  const ultima = ultimaSaudacao.get(chatId) || 0;
  if (agora - ultima > REPETIR_SAUDACAO_MIN * 60 * 1000) {
    ultimaSaudacao.set(chatId, agora);
    return MENU;
  }
  // Já saudado recentemente e não entendeu: reforça as opções de forma curta.
  return (
    `Não entendi 🤔. Escolha uma opção:\n\n` +
    `*1* Visto Portugal · *2* Juros abusivos · *3* Veículo/apreensão\n` +
    `Ou digite *DOC* (documentos) ou *VALORES* (honorários).`
  );
}

// ------------------------------------------------------------------
// Cliente do WhatsApp
// ------------------------------------------------------------------
const client = new Client({
  authStrategy: new LocalAuth({ dataPath: path.join(__dirname, ".wwebjs_auth") }),
  puppeteer: {
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  },
});

client.on("qr", (qr) => {
  console.log("\n📱  Escaneie o QR Code abaixo pelo WhatsApp:");
  console.log("    WhatsApp → Configurações → Aparelhos conectados → Conectar aparelho\n");
  qrcodeTerminal.generate(qr, { small: true });

  // Salva também um arquivo PNG (útil para escanear de outra tela)
  QRCode.toFile(path.join(__dirname, "qrcode-conexao.png"), qr, { width: 400 }, (err) => {
    if (!err) console.log("\n🖼️  Também salvei o QR em: bot-whatsapp/qrcode-conexao.png\n");
  });
});

client.on("authenticated", () => {
  console.log("🔐  Autenticado! A sessão ficará salva — não precisará escanear de novo.");
});

client.on("ready", () => {
  console.log(`\n✅  Robô da ${NOME_ESCRITORIO} conectado e atendendo!`);
  console.log("    Deixe esta janela aberta. Para parar, pressione Ctrl + C.\n");
});

client.on("auth_failure", (msg) => {
  console.error("❌  Falha de autenticação:", msg);
});

client.on("disconnected", (reason) => {
  console.warn("⚠️  Desconectado:", reason, "- reinicie o robô (npm start).");
});

client.on("message", async (msg) => {
  try {
    // Ignora grupos, status e mensagens do próprio número
    if (msg.fromMe) return;
    if (msg.from.endsWith("@g.us")) return;
    if (msg.from === "status@broadcast") return;
    if (msg.isStatus) return;

    const resposta = definirResposta(msg.body, msg.from);
    await msg.reply(resposta + RODAPE);
  } catch (err) {
    console.error("Erro ao responder:", err);
  }
});

client.initialize();
