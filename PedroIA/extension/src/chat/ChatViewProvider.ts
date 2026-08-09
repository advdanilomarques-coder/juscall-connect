import * as vscode from "vscode";
import { PedroIAClient, ChatMessage } from "../api/client";
import { buildContext } from "../utils/context";

interface WebviewMessage {
  type: string;
  text?: string;
  mode?: "auto" | "cloud" | "local";
}

/**
 * Renders the PedroIA chat inside the sidebar as a Webview, similar to
 * Copilot Chat / Claude Code. Keeps an in-memory history for the session.
 */
export class ChatViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "cleancode.chatView";

  private view?: vscode.WebviewView;
  private panel?: vscode.WebviewPanel;
  private history: ChatMessage[] = [];
  private readonly sessionId = `vscode-${Date.now()}`;

  constructor(
    private readonly extensionUri: vscode.Uri,
    private readonly client: PedroIAClient
  ) {}

  resolveWebviewView(webviewView: vscode.WebviewView): void {
    this.view = webviewView;
    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [vscode.Uri.joinPath(this.extensionUri, "media")],
    };
    webviewView.webview.html = this.getHtml(webviewView.webview);
    this.wire(webviewView.webview);
  }

  /** Opens the chat as a full editor tab (full screen). Shares history + logic. */
  public openInPanel(): void {
    if (this.panel) {
      this.panel.reveal(vscode.ViewColumn.Active);
      return;
    }
    this.panel = vscode.window.createWebviewPanel(
      "cleancode.chatPanel",
      "Clean Code — Chat",
      vscode.ViewColumn.Active,
      { enableScripts: true, retainContextWhenHidden: true, localResourceRoots: [vscode.Uri.joinPath(this.extensionUri, "media")] }
    );
    this.panel.webview.html = this.getHtml(this.panel.webview);
    this.wire(this.panel.webview);
    this.panel.onDidDispose(() => (this.panel = undefined));
  }

  /** Wires a webview's message handling (used by both the sidebar and the panel). */
  private wire(webview: vscode.Webview): void {
    webview.onDidReceiveMessage(async (msg: WebviewMessage) => {
      switch (msg.type) {
        case "sendMessage":
          await this.handleUserMessage(msg.text || "", msg.mode || "auto");
          break;
        case "clear":
          this.history = [];
          break;
        case "ready":
          this.checkBackend();
          break;
      }
    });
  }

  /** Public entry so commands can push a prompt into the chat (and send it). */
  public async ask(prompt: string): Promise<void> {
    await this.reveal();
    this.post({ type: "userEcho", text: prompt });
    await this.handleUserMessage(prompt, this.preferredMode());
  }

  /** Opens the chat and pre-fills the input with text (does NOT send) — "ask about my code". */
  public async prefill(text: string): Promise<void> {
    await this.reveal();
    this.post({ type: "prefill", text });
  }

  private async reveal(): Promise<void> {
    // If a full-screen panel is open, use it; otherwise reveal the sidebar view.
    if (this.panel) {
      this.panel.reveal(vscode.ViewColumn.Active);
      return;
    }
    if (!this.view) {
      await vscode.commands.executeCommand("cleancode.chatView.focus");
      await new Promise((r) => setTimeout(r, 350));
    }
    this.view?.show?.(true);
  }

  private preferredMode(): "auto" | "cloud" | "local" {
    return (
      (vscode.workspace.getConfiguration("cleancode").get<string>("preferredMode") as
        | "auto"
        | "cloud"
        | "local") || "auto"
    );
  }

  private async handleUserMessage(text: string, mode: "auto" | "cloud" | "local"): Promise<void> {
    if (!text.trim()) {
      return;
    }
    this.history.push({ role: "user", content: text });
    this.post({ type: "thinking" });

    try {
      const res = await this.client.chat({
        messages: this.history,
        mode,
        context: buildContext(),
        session_id: this.sessionId,
      });
      this.history.push({ role: "assistant", content: res.content });
      this.post({
        type: "assistant",
        text: res.content,
        meta: `${res.provider} · ${res.model} · ${res.mode}`,
      });
    } catch (err: any) {
      this.post({ type: "error", text: err?.message || String(err) });
    }
  }

  private async checkBackend(): Promise<void> {
    try {
      const h = await this.client.health();
      this.post({ type: "status", text: h.online ? "Online (nuvem disponível)" : "Offline (modo local)", ok: true });
    } catch {
      this.post({ type: "status", text: "Servidor Clean Code não encontrado — verifique a Backend Url nas configurações", ok: false });
    }
  }

  /** Posts to every open surface (sidebar view and/or full-screen panel). */
  private post(message: unknown): void {
    this.view?.webview.postMessage(message);
    this.panel?.webview.postMessage(message);
  }

  private getHtml(webview: vscode.Webview): string {
    const nonce = getNonce();
    const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, "media", "chat.css"));
    const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, "media", "chat.js"));
    const csp = [
      `default-src 'none'`,
      `style-src ${webview.cspSource}`,
      `script-src 'nonce-${nonce}'`,
      `font-src ${webview.cspSource}`,
    ].join("; ");

    return /* html */ `<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="Content-Security-Policy" content="${csp}" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link href="${styleUri}" rel="stylesheet" />
  <title>Clean Code</title>
</head>
<body>
  <header id="statusBar" class="status">Conectando…</header>
  <main id="messages" class="messages">
    <div class="welcome">
      <strong>Clean Code</strong>
      <p>Seu assistente de IA no VS Code. Peça para criar, corrigir, explicar, refatorar, documentar ou revisar código — em qualquer linguagem.</p>
      <p class="hint">Comandos: <code>/create</code> <code>/explain</code> <code>/fix</code> <code>/refactor</code> <code>/test</code> <code>/document</code> <code>/optimize</code> <code>/review</code> <code>/comment</code> <code>/convert</code> <code>/security</code></p>
      <p class="hint">Dica: selecione um código e aperte <code>Cmd/Ctrl+L</code> para perguntar sobre ele.</p>
    </div>
  </main>
  <footer class="composer">
    <select id="mode" title="Modo do modelo">
      <option value="auto">Auto</option>
      <option value="cloud">Cloud</option>
      <option value="local">Local</option>
    </select>
    <textarea id="input" rows="1" placeholder="Pergunte ao Clean Code… (Enter envia, Shift+Enter nova linha)"></textarea>
    <button id="send" title="Enviar">➤</button>
  </footer>
  <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
  }
}

function getNonce(): string {
  let text = "";
  const possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}
