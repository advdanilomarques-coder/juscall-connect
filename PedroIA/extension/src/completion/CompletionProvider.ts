import * as vscode from "vscode";
import { PedroIAClient } from "../api/client";

const MAX_PREFIX = 4000;
const MAX_SUFFIX = 1500;

/**
 * Clean Code Completion Engine — inline (ghost text) suggestions, tuned to feel
 * calm like GitHub Copilot:
 *  - debounced and cancellable (never fights the typist);
 *  - short by default (finish the current line/statement);
 *  - multi-line only when the context clearly opens a block;
 *  - output cleaned (no fences, no trailing junk, no echo of the prefix).
 */
export class CompletionProvider implements vscode.InlineCompletionItemProvider {
  private lastKey = "";
  private lastValue = "";

  constructor(private readonly client: PedroIAClient) {}

  private cfg<T>(key: string, dflt: T): T {
    return vscode.workspace.getConfiguration("cleancode").get<T>(key, dflt);
  }

  private get enabled(): boolean {
    return this.cfg("completion.enabled", true);
  }
  private get debounceMs(): number {
    return this.cfg("completion.debounceMs", 600);
  }
  private get mode(): "auto" | "cloud" | "local" {
    return this.cfg<string>("preferredMode", "auto") as "auto" | "cloud" | "local";
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

    const line = document.lineAt(position.line);
    const linePrefix = line.text.slice(0, position.character);
    const lineSuffix = line.text.slice(position.character);

    // Don't suggest on empty context, or when there is already code right after
    // the cursor on the same line (avoids messy mid-token insertions).
    if (!linePrefix.trim() && position.character === 0 && !document.getText().trim()) {
      return undefined;
    }
    if (lineSuffix.trim().length > 0 && /[\w)\]}"'`]$/.test(lineSuffix.trim())) {
      return undefined;
    }

    const prefix = document.getText(new vscode.Range(new vscode.Position(0, 0), position)).slice(-MAX_PREFIX);
    const suffix = document
      .getText(new vscode.Range(position, document.lineAt(document.lineCount - 1).range.end))
      .slice(0, MAX_SUFFIX);

    const key = `${document.uri.toString()}::${prefix.slice(-160)}`;
    if (key === this.lastKey && this.lastValue) {
      return [new vscode.InlineCompletionItem(this.lastValue, new vscode.Range(position, position))];
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
      const cleaned = this.postProcess(res.completion, linePrefix);
      if (!cleaned) {
        return undefined;
      }
      this.lastKey = key;
      this.lastValue = cleaned;
      return [new vscode.InlineCompletionItem(cleaned, new vscode.Range(position, position))];
    } catch {
      return undefined; // never interrupt typing
    }
  }

  /** Trim the model output to a Copilot-like size and remove noise. */
  private postProcess(raw: string, linePrefix: string): string {
    let text = raw.replace(/\r/g, "");

    // Strip a leading duplicate of what the user already typed on this line.
    const trimmedPrefix = linePrefix.trimStart();
    if (trimmedPrefix && text.startsWith(trimmedPrefix)) {
      text = text.slice(trimmedPrefix.length);
    }

    // Decide how many lines to allow, based on context.
    const opensBlock = /[:{([]\s*$/.test(linePrefix) || /=>\s*$/.test(linePrefix) || linePrefix.trim() === "";
    const maxLines = opensBlock ? 8 : 2;

    const lines = text.split("\n");
    const out: string[] = [];
    for (let i = 0; i < lines.length && out.length < maxLines; i++) {
      const l = lines[i];
      // Stop at a blank separator once we already have content.
      if (l.trim() === "" && out.length > 0) {
        break;
      }
      out.push(l);
    }
    let result = out.join("\n").replace(/\s+$/, "");

    // Single-line contexts: keep only the first line.
    if (!opensBlock && result.includes("\n")) {
      result = result.split("\n")[0];
    }
    return result;
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
