import Database from "better-sqlite3";
import { join } from "node:path";
import type { ForgeConfig } from "./config.js";
import { dataDir } from "./config.js";

export type DB = Database.Database;

let singleton: DB | null = null;

/**
 * Abre (e migra) o banco SQLite local. Tudo fica em ~/.forgemind/data/forgemind.sqlite.
 * 100% offline: nenhum servidor de banco, nenhum dado sai da maquina.
 */
export function openDatabase(cfg: ForgeConfig): DB {
  if (singleton) return singleton;
  const file = join(dataDir(cfg), "forgemind.sqlite");
  const db = new Database(file);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");
  db.pragma("synchronous = NORMAL");
  migrate(db);
  singleton = db;
  return db;
}

/** Migrations idempotentes versionadas via user_version. */
function migrate(db: DB): void {
  const current = db.pragma("user_version", { simple: true }) as number;

  const migrations: Array<() => void> = [
    // v1 — schema base
    () => {
      db.exec(`
        CREATE TABLE conversations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL DEFAULT 'Nova conversa',
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE messages (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
          role TEXT NOT NULL CHECK (role IN ('user','assistant','system')),
          content TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX idx_messages_conversation ON messages(conversation_id, id);

        -- Memoria de longo prazo pesquisavel/apagavel/exportavel (PDF item 12).
        CREATE TABLE memory (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          scope TEXT NOT NULL DEFAULT 'global',   -- global | project:<hash> | conversation:<id>
          kind  TEXT NOT NULL DEFAULT 'note',      -- note | fact | preference | project
          key   TEXT,
          value TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX idx_memory_scope ON memory(scope, kind);

        -- Indice incremental de projeto (PDF item 16/17).
        CREATE TABLE project_files (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          project TEXT NOT NULL,
          path TEXT NOT NULL,
          language TEXT,
          hash TEXT NOT NULL,
          size INTEGER NOT NULL DEFAULT 0,
          indexed_at TEXT NOT NULL DEFAULT (datetime('now')),
          UNIQUE(project, path)
        );
        CREATE TABLE project_symbols (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          file_id INTEGER NOT NULL REFERENCES project_files(id) ON DELETE CASCADE,
          name TEXT NOT NULL,
          kind TEXT NOT NULL,       -- function | class | interface | type | const | route | import
          line INTEGER NOT NULL DEFAULT 0,
          signature TEXT
        );
        CREATE INDEX idx_symbols_name ON project_symbols(name);
        CREATE INDEX idx_symbols_file ON project_symbols(file_id);
      `);
    },
    // v2 — full text search sobre memoria + mensagens
    () => {
      db.exec(`
        CREATE VIRTUAL TABLE memory_fts USING fts5(value, content='memory', content_rowid='id');
        CREATE TRIGGER memory_ai AFTER INSERT ON memory BEGIN
          INSERT INTO memory_fts(rowid, value) VALUES (new.id, new.value);
        END;
        CREATE TRIGGER memory_ad AFTER DELETE ON memory BEGIN
          INSERT INTO memory_fts(memory_fts, rowid, value) VALUES('delete', old.id, old.value);
        END;
        CREATE TRIGGER memory_au AFTER UPDATE ON memory BEGIN
          INSERT INTO memory_fts(memory_fts, rowid, value) VALUES('delete', old.id, old.value);
          INSERT INTO memory_fts(rowid, value) VALUES (new.id, new.value);
        END;
      `);
    },
    // v3 — grafo de dependencias (imports) para contexto cruzado (PDF item 17/18)
    () => {
      db.exec(`
        CREATE TABLE project_imports (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          file_id INTEGER NOT NULL REFERENCES project_files(id) ON DELETE CASCADE,
          module TEXT NOT NULL,          -- especificador cru: './foo', 'react', 'pkg/x'
          resolved_path TEXT,            -- caminho relativo resolvido no projeto (se local)
          names TEXT                     -- simbolos importados, separados por virgula
        );
        CREATE INDEX idx_imports_file ON project_imports(file_id);
        CREATE INDEX idx_imports_resolved ON project_imports(resolved_path);

        -- Marca exports para ranquear melhor o que e "API publica" de um arquivo.
        ALTER TABLE project_symbols ADD COLUMN exported INTEGER NOT NULL DEFAULT 0;
      `);
    },
  ];

  const tx = db.transaction((from: number) => {
    for (let v = from; v < migrations.length; v++) {
      migrations[v]!();
      db.pragma(`user_version = ${v + 1}`);
    }
  });
  tx(current);
}

/** Fecha o banco (usado em testes e shutdown). */
export function closeDatabase(): void {
  if (singleton) {
    singleton.close();
    singleton = null;
  }
}
