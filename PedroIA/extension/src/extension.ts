/**
 * PedroIA — Extensão do VS Code
 * ------------------------------------------------------------------
 * - Chat com o PedroIA (webview + streaming)
 * - "Explicar seleção" no menu de contexto
 * - Autocomplete inline estilo Copilot (InlineCompletionItemProvider)
 *
 * Toda a inteligência vem do backend (ver ../backend). A extensão nunca
 * guarda a chave da Anthropic — apenas a "chave de acesso" do seu backend.
 */
import * as vscode from "vscode";

type ChatMessage = { role: "user" | "assistant"; content: string };

function cfg() {
  const c = vscode.workspace.getConfiguration("pedroia");
  return {
    backendUrl: (c.get<string>("backendUrl") || "").replace(/\/+$/, ""),
    apiKey: c.get<string>("apiKey") || "",
    enableAutocomplete: c.get<boolean>("enableAutocomplete") ?? true,
    debounceMs: c.get<number>("autocompleteDebounceMs") ?? 400,
  };
}

function headers() {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  const { apiKey } = cfg();
  if (apiKey) h["x-pedroia-key"] = apiKey;
  return h;
}

// ------------------------------------------------------------------
// Ativação
// ------------------------------------------------------------------
export function activate(context: vscode.ExtensionContext) {
  const chat = new ChatPanel(context);

  context.subscriptions.push(
    vscode.commands.registerCommand("pedroia.ask", () => chat.reveal()),

    vscode.commands.registerCommand("pedroia.explainSelection", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;
      const code = editor.document.getText(editor.selection) || editor.document.getText();
      const lang = editor.document.languageId;
      chat.reveal();
      chat.ask(`Explique este código (${lang}) de forma clara e aponte possíveis problemas:\n\n\`\`\`${lang}\n${code}\n\`\`\``);
    }),

    vscode.commands.registerCommand("pedroia.toggleAutocomplete", async () => {
      const c = vscode.workspace.getConfiguration("pedroia");
      const next = !(c.get<boolean>("enableAutocomplete") ?? true);
      await c.update("enableAutocomplete", next, vscode.ConfigurationTarget.Global);
      vscode.window.showInformationMessage(`PedroIA autocomplete: ${next ? "ATIVADO" : "desativado"}`);
    })
  );

  // Autocomplete inline (todas as linguagens)
  const provider = new PedroIACompletionProvider();
  context.subscriptions.push(
    vscode.languages.registerInlineCompletionItemProvider({ pattern: "**" }, provider)
  );
}

export function deactivate() {}

// ------------------------------------------------------------------
// Autocomplete inline (estilo Copilot)
// ------------------------------------------------------------------
class PedroIACompletionProvider implements vscode.InlineCompletionItemProvider {
  private timer: NodeJS.Timeout | undefined;

  async provideInlineCompletionItems(
    document: vscode.TextDocument,
    position: vscode.Position,
    _context: vscode.InlineCompletionContext,
    token: vscode.CancellationToken
  ): Promise<vscode.InlineCompletionItem[] | undefined> {
    const { backendUrl, enableAutocomplete, debounceMs } = cfg();
    if (!enableAutocomplete || !backendUrl) return;

    // Debounce: espera o usuário parar de digitar
    await new Promise<void>((resolve) => {
      if (this.timer) clearTimeout(this.timer);
      this.timer = setTimeout(resolve, debounceMs);
    });
    if (token.isCancellationRequested) return;

    // Contexto ao redor do cursor (limitado para não gastar tokens à toa)
    const maxLines = 80;
    const startLine = Math.max(0, position.line - maxLines);
    const prefixRange = new vscode.Range(new vscode.Position(startLine, 0), position);
    const prefix = document.getText(prefixRange);
    const endLine = Math.min(document.lineCount - 1, position.line + 20);
    const suffixRange = new vscode.Range(position, document.lineAt(endLine).range.end);
    const suffix = document.getText(suffixRange);

    if (prefix.trim().length < 2) return;

    try {
      const resp = await fetch(`${backendUrl}/v1/complete`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({ prefix, suffix, language: document.languageId }),
      });
      if (!resp.ok || token.isCancellationRequested) return;
      const data = (await resp.json()) as { completion?: string };
      const completion = (data.completion || "").replace(/\s+$/, "");
      if (!completion) return;
      return [new vscode.InlineCompletionItem(completion, new vscode.Range(position, position))];
    } catch {
      return; // silencioso: autocomplete nunca deve atrapalhar a digitação
    }
  }
}

// ------------------------------------------------------------------
// Painel de chat (webview + streaming SSE)
// ------------------------------------------------------------------
class ChatPanel {
  private panel: vscode.WebviewPanel | undefined;
  private history: ChatMessage[] = [];

  constructor(private context: vscode.ExtensionContext) {}

  reveal() {
    if (this.panel) {
      this.panel.reveal(vscode.ViewColumn.Beside);
      return;
    }
    this.panel = vscode.window.createWebviewPanel(
      "pedroiaChat",
      "PedroIA",
      vscode.ViewColumn.Beside,
      { enableScripts: true, retainContextWhenHidden: true }
    );
    this.panel.iconPath = vscode.Uri.joinPath(this.context.extensionUri, "icon.png");
    this.panel.webview.html = this.html();
    this.panel.onDidDispose(() => (this.panel = undefined));
    this.panel.webview.onDidReceiveMessage((m) => {
      if (m.type === "send") this.ask(m.text);
    });
  }

  ask(text: string) {
    if (!this.panel) this.reveal();
    const { backendUrl } = cfg();
    if (!backendUrl) {
      vscode.window.showErrorMessage("Configure 'pedroia.backendUrl' nas configurações.");
      return;
    }
    this.post({ type: "user", text });
    this.history.push({ role: "user", content: text });
    this.stream();
  }

  private async stream() {
    const { backendUrl } = cfg();
    this.post({ type: "assistant_start" });
    let assistant = "";
    try {
      const resp = await fetch(`${backendUrl}/v1/chat`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({ messages: this.history }),
      });
      if (!resp.ok || !resp.body) {
        const msg = await resp.text().catch(() => "");
        this.post({ type: "assistant_delta", text: `\n\n⚠️ Erro ${resp.status}. ${msg}` });
        this.post({ type: "assistant_end" });
        return;
      }
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() || "";
        for (const ev of events) {
          const lines = ev.split("\n");
          const eventLine = lines.find((l) => l.startsWith("event:"));
          const dataLine = lines.find((l) => l.startsWith("data:"));
          if (!eventLine || !dataLine) continue;
          const name = eventLine.slice(6).trim();
          const data = JSON.parse(dataLine.slice(5).trim());
          if (name === "delta") {
            assistant += data.text;
            this.post({ type: "assistant_delta", text: data.text });
          } else if (name === "error") {
            this.post({ type: "assistant_delta", text: `\n\n⚠️ ${data.message}` });
          }
        }
      }
      this.history.push({ role: "assistant", content: assistant });
      this.post({ type: "assistant_end" });
    } catch (err: any) {
      this.post({ type: "assistant_delta", text: `\n\n⚠️ Falha de conexão: ${err?.message}` });
      this.post({ type: "assistant_end" });
    }
  }

  private post(msg: unknown) {
    this.panel?.webview.postMessage(msg);
  }

  private html() {
    return /* html */ `<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  :root { color-scheme: light dark; }
  body { font-family: var(--vscode-font-family); margin: 0; display: flex; flex-direction: column; height: 100vh; }
  #log { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
  .msg { padding: 10px 14px; border-radius: 12px; max-width: 100%; white-space: pre-wrap; line-height: 1.5; }
  .user { align-self: flex-end; background: var(--vscode-button-background); color: var(--vscode-button-foreground); }
  .assistant { align-self: flex-start; background: var(--vscode-editor-inactiveSelectionBackground); }
  .assistant pre { background: rgba(0,0,0,.35); padding: 10px; border-radius: 8px; overflow-x: auto; }
  #bar { display: flex; gap: 8px; padding: 12px; border-top: 1px solid var(--vscode-panel-border); }
  #input { flex: 1; resize: none; padding: 8px; border-radius: 8px; border: 1px solid var(--vscode-input-border);
           background: var(--vscode-input-background); color: var(--vscode-input-foreground); font-family: inherit; }
  #send { padding: 0 16px; border: none; border-radius: 8px; cursor: pointer;
          background: var(--vscode-button-background); color: var(--vscode-button-foreground); }
  .empty { opacity: .6; text-align: center; margin-top: 40px; }
</style>
</head>
<body>
  <div id="log"><div class="empty">👋 Olá! Sou o <b>PedroIA</b>. Pergunte qualquer coisa sobre o seu código.</div></div>
  <div id="bar">
    <textarea id="input" rows="2" placeholder="Pergunte ao PedroIA... (Enter para enviar)"></textarea>
    <button id="send">Enviar</button>
  </div>
<script>
  const vscode = acquireVsCodeApi();
  const log = document.getElementById('log');
  const input = document.getElementById('input');
  const send = document.getElementById('send');
  let current = null;

  function esc(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function render(el, text){
    // markdown mínimo: blocos de código
    el.innerHTML = esc(text).replace(/\`\`\`(\\w*)\\n([\\s\\S]*?)\`\`\`/g, (_m,_l,c)=>'<pre>'+c+'</pre>');
    log.scrollTop = log.scrollHeight;
  }
  function addMsg(cls){ const d=document.createElement('div'); d.className='msg '+cls; log.appendChild(d); return d; }

  function doSend(){
    const text = input.value.trim();
    if(!text) return;
    const empty = log.querySelector('.empty'); if(empty) empty.remove();
    const u = addMsg('user'); u.textContent = text;
    input.value = '';
    vscode.postMessage({ type:'send', text });
    log.scrollTop = log.scrollHeight;
  }
  send.addEventListener('click', doSend);
  input.addEventListener('keydown', e => { if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); doSend(); } });

  window.addEventListener('message', e => {
    const m = e.data;
    if(m.type==='assistant_start'){ current = { el: addMsg('assistant'), text: '' }; render(current.el, '▍'); }
    else if(m.type==='assistant_delta' && current){ current.text += m.text; render(current.el, current.text + '▍'); }
    else if(m.type==='assistant_end' && current){ render(current.el, current.text); current = null; }
  });
</script>
</body>
</html>`;
  }
}
