import * as vscode from "vscode";
import { PedroIAClient } from "./api/client";
import { ChatViewProvider } from "./chat/ChatViewProvider";
import { CompletionProvider } from "./completion/CompletionProvider";
import { registerCommands } from "./commands";

export function activate(context: vscode.ExtensionContext): void {
  const client = new PedroIAClient();

  // Sidebar chat.
  const chatProvider = new ChatViewProvider(context.extensionUri, client);
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(ChatViewProvider.viewType, chatProvider, {
      webviewOptions: { retainContextWhenHidden: true },
    })
  );

  // Inline completion (Copilot-style ghost text).
  const completion = new CompletionProvider(client);
  context.subscriptions.push(
    vscode.languages.registerInlineCompletionItemProvider({ pattern: "**" }, completion)
  );

  // Commands + context menu.
  registerCommands(context, chatProvider);

  const status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  status.text = "$(sparkle) PedroIA";
  status.tooltip = "Abrir o chat do PedroIA";
  status.command = "pedroia.openChat";
  status.show();
  context.subscriptions.push(status);

  console.log("PedroIA ativado.");
}

export function deactivate(): void {
  // no-op
}
