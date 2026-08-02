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
  public static readonly viewType = "pedroia.chatView";

  private view?: vscode.WebviewView;
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

    webviewView.webview.onDidReceiveMessage(async (msg: WebviewMessage) => {
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

  /** Public entry so commands can push a prompt into the chat. */
  public async ask(prompt: string): Promise<void> {
    if (!this.view) {
      await vscode.commands.executeCommand("pedroia.chatView.focus");
      // Give the webview a moment to resolve.
      await new Promise((r) => setTimeout(r, 300));
    }
    this.view?.show?.(true);
    this.post({ type: "userEcho", text: prompt });
    await this.handleUserMessage(prompt, this.preferredMode());
  }

  private preferredMode(): "auto" | "cloud" | "local" {
    return (
      (vscode.workspace.getConfiguration("pedroia").get<string>("preferredMode") as
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
      this.post({ type: "status", text: h.online ? "Online (cloud disponível)" : "Offline (modo local)", ok: true });
    } catch {
      this.post({ type: "status", text: "Backend não encontrado — inicie o servidor PedroIA", ok: false });
    }
  }

  private post(message: unknown): void {
    this.view?.webview.postMessage(message);
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
  <title>PedroIA</title>
</head>
<body>
  <header id="statusBar" class="status">Conectando…</header>
  <main id="messages" class="messages">
    <div class="welcome">
      <strong>PedroIA</strong>
      <p>Seu engenheiro de IA dentro do VS Code. Peça para criar, corrigir, explicar ou refatorar código.</p>
      <p class="hint">Comandos: <code>/create</code> <code>/explain</code> <code>/fix</code> <code>/refactor</code> <code>/test</code> <code>/security</code></p>
    </div>
  </main>
  <footer class="composer">
    <select id="mode" title="Modo do modelo">
      <option value="auto">Auto</option>
      <option value="cloud">Cloud</option>
      <option value="local">Local</option>
    </select>
    <textarea id="input" rows="1" placeholder="Pergunte ao PedroIA… (Enter para enviar, Shift+Enter para nova linha)"></textarea>
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
