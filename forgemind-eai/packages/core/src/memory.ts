import type { DB } from "./db.js";

export interface Message {
  id: number;
  conversation_id: number;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface MemoryItem {
  id: number;
  scope: string;
  kind: string;
  key: string | null;
  value: string;
  created_at: string;
}

/**
 * Camada de memoria e historico (PDF item 12). Tudo local, pesquisavel,
 * controlavel, apagavel e exportavel.
 */
export class MemoryStore {
  constructor(private readonly db: DB) {}

  // ---- Conversas / historico ----
  createConversation(title = "Nova conversa"): Conversation {
    const info = this.db.prepare("INSERT INTO conversations (title) VALUES (?)").run(title);
    return this.getConversation(Number(info.lastInsertRowid))!;
  }

  getConversation(id: number): Conversation | undefined {
    return this.db.prepare("SELECT * FROM conversations WHERE id = ?").get(id) as Conversation | undefined;
  }

  listConversations(limit = 50): Conversation[] {
    return this.db
      .prepare("SELECT * FROM conversations ORDER BY updated_at DESC LIMIT ?")
      .all(limit) as Conversation[];
  }

  addMessage(conversationId: number, role: Message["role"], content: string): Message {
    const info = this.db
      .prepare("INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)")
      .run(conversationId, role, content);
    this.db.prepare("UPDATE conversations SET updated_at = datetime('now') WHERE id = ?").run(conversationId);
    return this.db.prepare("SELECT * FROM messages WHERE id = ?").get(Number(info.lastInsertRowid)) as Message;
  }

  getMessages(conversationId: number, limit = 200): Message[] {
    return this.db
      .prepare("SELECT * FROM messages WHERE conversation_id = ? ORDER BY id ASC LIMIT ?")
      .all(conversationId, limit) as Message[];
  }

  deleteConversation(id: number): void {
    this.db.prepare("DELETE FROM conversations WHERE id = ?").run(id);
  }

  // ---- Memoria de longo prazo ----
  remember(value: string, opts: { scope?: string; kind?: string; key?: string } = {}): MemoryItem {
    const info = this.db
      .prepare("INSERT INTO memory (scope, kind, key, value) VALUES (?, ?, ?, ?)")
      .run(opts.scope ?? "global", opts.kind ?? "note", opts.key ?? null, value);
    return this.db.prepare("SELECT * FROM memory WHERE id = ?").get(Number(info.lastInsertRowid)) as MemoryItem;
  }

  searchMemory(query: string, limit = 20): MemoryItem[] {
    const q = query.trim();
    if (!q) return this.db.prepare("SELECT * FROM memory ORDER BY id DESC LIMIT ?").all(limit) as MemoryItem[];
    try {
      return this.db
        .prepare(
          `SELECT m.* FROM memory_fts f
           JOIN memory m ON m.id = f.rowid
           WHERE memory_fts MATCH ?
           ORDER BY rank LIMIT ?`,
        )
        .all(q.replace(/["]/g, "") + "*", limit) as MemoryItem[];
    } catch {
      // fallback LIKE se o FTS reclamar da query
      return this.db
        .prepare("SELECT * FROM memory WHERE value LIKE ? ORDER BY id DESC LIMIT ?")
        .all(`%${q}%`, limit) as MemoryItem[];
    }
  }

  listMemory(scope?: string, limit = 100): MemoryItem[] {
    if (scope) {
      return this.db
        .prepare("SELECT * FROM memory WHERE scope = ? ORDER BY id DESC LIMIT ?")
        .all(scope, limit) as MemoryItem[];
    }
    return this.db.prepare("SELECT * FROM memory ORDER BY id DESC LIMIT ?").all(limit) as MemoryItem[];
  }

  forget(id: number): void {
    this.db.prepare("DELETE FROM memory WHERE id = ?").run(id);
  }

  /** Exporta memoria + conversas para um objeto serializavel (JSON). */
  export(): { conversations: Conversation[]; messages: Message[]; memory: MemoryItem[] } {
    return {
      conversations: this.db.prepare("SELECT * FROM conversations").all() as Conversation[],
      messages: this.db.prepare("SELECT * FROM messages").all() as Message[],
      memory: this.db.prepare("SELECT * FROM memory").all() as MemoryItem[],
    };
  }
}
