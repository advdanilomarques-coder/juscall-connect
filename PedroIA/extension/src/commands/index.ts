import * as vscode from "vscode";
import { ChatViewProvider } from "../chat/ChatViewProvider";
import { getSelectionOrDocument } from "../utils/context";

/**
 * Slash-style commands routed into the chat. Each command builds a focused
 * prompt from the current editor selection so the user does not have to
 * paste code manually.
 */
export function registerCommands(context: vscode.ExtensionContext, chat: ChatViewProvider): void {
  const focusChat = () => vscode.commands.executeCommand("cleancode.chatView.focus");

  context.subscriptions.push(
    vscode.commands.registerCommand("cleancode.openChat", focusChat),
    vscode.commands.registerCommand("cleancode.openChatFullscreen", () => chat.openInPanel()),

    // Blackbox-style: open the chat with the current code attached, ready for your question.
    vscode.commands.registerCommand("cleancode.askSelection", async () => {
      const sel = getSelectionOrDocument();
      if (!sel) {
        await focusChat();
        return;
      }
      const attached = `Sobre este trecho de ${sel.relPath} (${sel.language}):\n\n\`\`\`${sel.language}\n${sel.text}\n\`\`\`\n\nMinha pergunta: `;
      await chat.prefill(attached);
    }),

    vscode.commands.registerCommand("cleancode.create", async () => {
      const what = await vscode.window.showInputBox({
        prompt: "O que o Clean Code deve criar?",
        placeHolder: "Ex.: uma API REST de tarefas em FastAPI com autenticação JWT",
      });
      if (what) {
        await chat.ask(`/create ${what}`);
      }
    }),

    vscode.commands.registerCommand("cleancode.convert", async () => {
      const sel = getSelectionOrDocument();
      if (!sel) {
        vscode.window.showInformationMessage("Selecione o código que deseja converter.");
        return;
      }
      const target = await vscode.window.showInputBox({
        prompt: "Converter para qual linguagem?",
        placeHolder: "Ex.: Python, TypeScript, Go, Rust…",
      });
      if (!target) {
        return;
      }
      const prompt = `/convert Converta este código de ${sel.language} para ${target}, mantendo o comportamento.\n\nArquivo: ${sel.relPath}\n\n\`\`\`${sel.language}\n${sel.text}\n\`\`\``;
      await chat.ask(prompt);
    }),

    // Reads the current terminal selection and asks for help (explain/fix).
    vscode.commands.registerCommand("cleancode.terminalHelp", async () => {
      const term = vscode.window.activeTerminal;
      if (!term) {
        vscode.window.showInformationMessage("Abra um terminal e selecione o texto (comando ou erro) primeiro.");
        return;
      }
      const before = await vscode.env.clipboard.readText();
      await vscode.commands.executeCommand("workbench.action.terminal.copySelection");
      // Give the clipboard a moment to update before reading it back.
      await new Promise((r) => setTimeout(r, 150));
      const selection = (await vscode.env.clipboard.readText()).trim();
      // Restore the user's previous clipboard content.
      if (before !== selection) {
        await vscode.env.clipboard.writeText(before);
      }

      if (!selection || selection === before) {
        const typed = await vscode.window.showInputBox({
          prompt: "Cole o comando ou erro do terminal para o Clean Code ajudar",
          placeHolder: "Ex.: npm ERR! code ELIFECYCLE …",
        });
        if (!typed) {
          return;
        }
        await chat.ask(terminalPrompt(typed));
        return;
      }
      await chat.ask(terminalPrompt(selection));
    }),

    vscode.commands.registerCommand("cleancode.explain", () => runOnSelection(chat, "/explain", "Explique este código de forma objetiva")),
    vscode.commands.registerCommand("cleancode.fix", () => runOnSelection(chat, "/fix", "Corrija os erros neste código e explique a correção em 1 linha")),
    vscode.commands.registerCommand("cleancode.refactor", () => runOnSelection(chat, "/refactor", "Refatore este código melhorando legibilidade e desempenho")),
    vscode.commands.registerCommand("cleancode.test", () => runOnSelection(chat, "/test", "Crie testes automatizados para este código")),
    vscode.commands.registerCommand("cleancode.security", () => runOnSelection(chat, "/security", "Analise este código em busca de vulnerabilidades")),
    vscode.commands.registerCommand("cleancode.document", () => runOnSelection(chat, "/document", "Gere documentação/docstrings para este código")),
    vscode.commands.registerCommand("cleancode.optimize", () => runOnSelection(chat, "/optimize", "Otimize o desempenho deste código, apontando os ganhos")),
    vscode.commands.registerCommand("cleancode.review", () => runOnSelection(chat, "/review", "Faça uma revisão de código (code review) apontando problemas e melhorias")),
    vscode.commands.registerCommand("cleancode.comment", () => runOnSelection(chat, "/comment", "Adicione comentários claros explicando este código"))
  );
}

function terminalPrompt(content: string): string {
  return `/terminal Explique o que está acontecendo neste terminal e, se houver erro, diga o comando exato para resolver.\n\n\`\`\`\n${content}\n\`\`\``;
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
