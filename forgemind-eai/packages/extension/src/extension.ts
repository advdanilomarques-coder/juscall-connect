import * as vscode from "vscode";

/**
 * ForgeMind EAI — extensao VS Code.
 * Fina por design: toda a inteligencia vive no backend local (offline).
 * A extensao so orquestra Ghost Text, chat e comandos.
 */

function serverUrl(): string {
  return vscode.workspace.getConfiguration("forgemind").get<string>("serverUrl", "http://127.0.0.1:4319");
}

export function activate(context: vscode.ExtensionContext): void {
  // -------- Ghost Text (inline completion) com debounce/cancelamento --------
  const provider: vscode.InlineCompletionItemProvider = {
    async provideInlineCompletionItems(document, position, _ctx, token) {
      const cfg = vscode.workspace.getConfiguration("forgemind");
      if (!cfg.get<boolean>("inlineEnabled", true)) return { items: [] };

      // debounce natural: espera uma pausa curta antes de pedir
      await new Promise((r) => setTimeout(r, 250));
      if (token.isCancellationRequested) return { items: [] };

      const prefix = document.getText(
        new vscode.Range(new vscode.Position(Math.max(0, position.line - 60), 0), position),
      );
      const suffix = document.getText(
        new vscode.Range(position, new vscode.Position(position.line + 20, 0)),
      );

      try {
        const controller = new AbortController();
        token.onCancellationRequested(() => controller.abort());
        const res = await fetch(`${serverUrl()}/api/complete`, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            prefix,
            suffix,
            language: document.languageId,
            path: document.uri.fsPath,
            projectRoot: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
          }),
          signal: controller.signal,
        });
        if (!res.ok) return { items: [] };
        const data = (await res.json()) as { text: string; confidence: number };
        if (!data.text) return { items: [] };
        return {
          items: [{ insertText: data.text, range: new vscode.Range(position, position) }],
        };
      } catch {
        return { items: [] };
      }
    },
  };
  context.subscriptions.push(
    vscode.languages.registerInlineCompletionItemProvider({ pattern: "**" }, provider),
  );

  // -------- Comando: chat --------
  context.subscriptions.push(
    vscode.commands.registerCommand("forgemind.chat", () => {
      const panel = vscode.window.createWebviewPanel("forgemindChat", "ForgeMind Chat", vscode.ViewColumn.Beside, {
        enableScripts: true,
      });
      panel.webview.html = chatHtml(serverUrl());
    }),
  );

  // -------- Comando: explicar selecao --------
  context.subscriptions.push(
    vscode.commands.registerCommand("forgemind.explainSelection", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;
      const code = editor.document.getText(editor.selection) || editor.document.getText();
      const out = vscode.window.createOutputChannel("ForgeMind");
      out.show(true);
      out.appendLine("◆ ForgeMind — explicando seleção...\n");
      try {
        const res = await fetch(`${serverUrl()}/api/chat`, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            messages: [{ role: "user", content: `Explique este código:\n\n${code}` }],
          }),
        });
        const reader = res.body?.getReader();
        const dec = new TextDecoder();
        if (reader) {
          for (;;) {
            const { done, value } = await reader.read();
            if (done) break;
            for (const line of dec.decode(value).split("\n\n")) {
              const t = line.trim();
              if (t.startsWith("data:") && t.slice(5).trim() !== "[DONE]") {
                try {
                  const o = JSON.parse(t.slice(5));
                  if (o.delta) out.append(o.delta);
                } catch {
                  /* ignore */
                }
              }
            }
          }
        }
        out.appendLine("\n");
      } catch (e) {
        out.appendLine(`[erro] backend ForgeMind offline? ${(e as Error).message}`);
      }
    }),
  );

  // -------- Comando: abrir site --------
  context.subscriptions.push(
    vscode.commands.registerCommand("forgemind.openSite", () => {
      vscode.env.openExternal(vscode.Uri.parse(serverUrl()));
    }),
  );

  // -------- Comando: indexar projeto (contexto cruzado do inline) --------
  const indexProject = async (silent = false) => {
    const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!root) return;
    try {
      const res = await fetch(`${serverUrl()}/api/index`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ root }),
      });
      const data = (await res.json()) as { files?: number; symbols?: number; error?: string };
      if (!silent) {
        vscode.window.showInformationMessage(
          data.error ? `ForgeMind: ${data.error}` : `ForgeMind indexou ${data.files} arquivos, ${data.symbols} símbolos.`,
        );
      }
    } catch {
      if (!silent) vscode.window.showWarningMessage("ForgeMind: backend offline? Rode `forgemind start`.");
    }
  };
  context.subscriptions.push(
    vscode.commands.registerCommand("forgemind.indexProject", () => indexProject(false)),
  );
  // Auto-indexa ao abrir (silencioso) para que o inline tenha contexto do projeto.
  void indexProject(true);

  const status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  status.text = "$(flame) ForgeMind";
  status.tooltip = "ForgeMind EAI — chat";
  status.command = "forgemind.chat";
  status.show();
  context.subscriptions.push(status);
}

export function deactivate(): void {
  /* nada a limpar */
}

function chatHtml(url: string): string {
  // Webview minima que embute o site local do ForgeMind.
  return `<!doctype html><html><head><meta charset="utf-8"/>
  <style>html,body,iframe{margin:0;height:100%;width:100%;border:0;background:#17161a}</style>
  </head><body><iframe src="${url}" sandbox="allow-scripts allow-same-origin allow-forms"></iframe></body></html>`;
}
