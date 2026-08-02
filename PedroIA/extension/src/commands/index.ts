import * as vscode from "vscode";
import { ChatViewProvider } from "../chat/ChatViewProvider";
import { getSelectionOrDocument } from "../utils/context";

/**
 * Slash-style commands routed into the chat. Each command builds a focused
 * prompt from the current editor selection so the user does not have to
 * paste code manually.
 */
export function registerCommands(context: vscode.ExtensionContext, chat: ChatViewProvider): void {
  const focusChat = async () => {
    await vscode.commands.executeCommand("pedroia.chatView.focus");
  };

  context.subscriptions.push(
    vscode.commands.registerCommand("pedroia.openChat", focusChat),

    vscode.commands.registerCommand("pedroia.create", async () => {
      const what = await vscode.window.showInputBox({
        prompt: "O que o PedroIA deve criar?",
        placeHolder: "Ex.: sistema financeiro completo em Python com FastAPI",
      });
      if (what) {
        await chat.ask(`/create ${what}`);
      }
    }),

    vscode.commands.registerCommand("pedroia.explain", () => runOnSelection(chat, "/explain", "Explique este código em detalhes")),
    vscode.commands.registerCommand("pedroia.fix", () => runOnSelection(chat, "/fix", "Corrija os erros neste código e explique a correção")),
    vscode.commands.registerCommand("pedroia.refactor", () => runOnSelection(chat, "/refactor", "Refatore este código melhorando legibilidade e desempenho")),
    vscode.commands.registerCommand("pedroia.test", () => runOnSelection(chat, "/test", "Crie testes automatizados para este código")),
    vscode.commands.registerCommand("pedroia.security", () => runOnSelection(chat, "/security", "Analise este código em busca de vulnerabilidades de segurança"))
  );
}

async function runOnSelection(chat: ChatViewProvider, slash: string, instruction: string): Promise<void> {
  const sel = getSelectionOrDocument();
  if (!sel) {
    await chat.ask(`${slash} ${instruction}`);
    return;
  }
  const prompt = `${slash} ${instruction}.\n\nArquivo: ${sel.relPath} (${sel.language})\n\n\`\`\`${sel.language}\n${sel.text}\n\`\`\``;
  await chat.ask(prompt);
}
