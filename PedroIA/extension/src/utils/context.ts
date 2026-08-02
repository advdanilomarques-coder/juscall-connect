import * as vscode from "vscode";
import { ProjectContext } from "../api/client";

/**
 * Builds project/editor context automatically — the "understand context like Copilot"
 * behavior. The user does not need to paste huge prompts; PedroIA reads the active
 * editor, selection, diagnostics and workspace on its own.
 */
export function buildContext(): ProjectContext {
  const editor = vscode.window.activeTextEditor;
  const ctx: ProjectContext = {
    workspace_name: vscode.workspace.name,
    open_files: vscode.workspace.textDocuments
      .filter((d) => !d.isUntitled && d.uri.scheme === "file")
      .map((d) => vscode.workspace.asRelativePath(d.uri))
      .slice(0, 25),
  };

  if (editor) {
    const doc = editor.document;
    ctx.file_path = vscode.workspace.asRelativePath(doc.uri);
    ctx.language = doc.languageId;

    const sel = editor.selection;
    if (!sel.isEmpty) {
      ctx.selection = doc.getText(sel);
    }

    const diags = vscode.languages.getDiagnostics(doc.uri);
    ctx.diagnostics = diags
      .filter((d) => d.severity === vscode.DiagnosticSeverity.Error || d.severity === vscode.DiagnosticSeverity.Warning)
      .slice(0, 30)
      .map((d) => `L${d.range.start.line + 1}: ${vscode.DiagnosticSeverity[d.severity]}: ${d.message}`);
  }

  return ctx;
}

/** Returns selected text, or the whole document if nothing is selected. */
export function getSelectionOrDocument(): { text: string; language: string; relPath: string } | undefined {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    return undefined;
  }
  const doc = editor.document;
  const sel = editor.selection;
  const text = sel.isEmpty ? doc.getText() : doc.getText(sel);
  return {
    text,
    language: doc.languageId,
    relPath: vscode.workspace.asRelativePath(doc.uri),
  };
}
