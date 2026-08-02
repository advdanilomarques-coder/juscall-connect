import * as vscode from "vscode";
import { PedroIAClient } from "../api/client";

const MAX_PREFIX = 3000;
const MAX_SUFFIX = 1000;

/**
 * PedroIA Code Completion Engine — inline (ghost text) suggestions, similar to
 * GitHub Copilot. Requests are debounced and cancellable; a small cache avoids
 * re-querying identical contexts.
 */
export class CompletionProvider implements vscode.InlineCompletionItemProvider {
  private lastKey = "";
  private lastValue = "";

  constructor(private readonly client: PedroIAClient) {}

  private get enabled(): boolean {
    return vscode.workspace.getConfiguration("pedroia").get<boolean>("completion.enabled", true);
  }

  private get debounceMs(): number {
    return vscode.workspace.getConfiguration("pedroia").get<number>("completion.debounceMs", 350);
  }

  private get mode(): "auto" | "cloud" | "local" {
    return (
      (vscode.workspace.getConfiguration("pedroia").get<string>("preferredMode") as
        | "auto"
        | "cloud"
        | "local") || "auto"
    );
  }

  async provideInlineCompletionItems(
    document: vscode.TextDocument,
    position: vscode.Position,
    _context: vscode.InlineCompletionContext,
    token: vscode.CancellationToken
  ): Promise<vscode.InlineCompletionItem[] | undefined> {
    if (!this.enabled || token.isCancellationRequested) {
      return undefined;
    }

    const prefix = document.getText(new vscode.Range(new vscode.Position(0, 0), position)).slice(-MAX_PREFIX);
    const suffix = document
      .getText(new vscode.Range(position, document.lineAt(document.lineCount - 1).range.end))
      .slice(0, MAX_SUFFIX);

    // Don't fire on empty lines with no leading context.
    if (!prefix.trim()) {
      return undefined;
    }

    const key = `${document.uri.toString()}::${prefix.slice(-120)}`;
    if (key === this.lastKey && this.lastValue) {
      return [new vscode.InlineCompletionItem(this.lastValue)];
    }

    await this.delay(this.debounceMs, token);
    if (token.isCancellationRequested) {
      return undefined;
    }

    try {
      const res = await this.client.complete({
        prefix,
        suffix,
        language: document.languageId,
        file_path: vscode.workspace.asRelativePath(document.uri),
        mode: this.mode,
      });
      if (token.isCancellationRequested || !res.completion) {
        return undefined;
      }
      this.lastKey = key;
      this.lastValue = res.completion;
      return [new vscode.InlineCompletionItem(res.completion, new vscode.Range(position, position))];
    } catch {
      // Silent failure — completion must never interrupt typing.
      return undefined;
    }
  }

  private delay(ms: number, token: vscode.CancellationToken): Promise<void> {
    return new Promise((resolve) => {
      const t = setTimeout(resolve, ms);
      token.onCancellationRequested(() => {
        clearTimeout(t);
        resolve();
      });
    });
  }
}
