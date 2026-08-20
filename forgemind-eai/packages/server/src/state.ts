import {
  createProvider,
  loadConfig,
  openDatabase,
  MemoryStore,
  CompletionCache,
  type AIProvider,
  type ForgeConfig,
  type DB,
} from "@forgemind/core";

/**
 * Estado compartilhado do servidor. O provider e recriado quando o nome muda
 * (troca via /api/config), preservando cache do modelo local enquanto o mesmo.
 */
export class ServerState {
  config: ForgeConfig;
  db: DB;
  memory: MemoryStore;
  completionCache = new CompletionCache();
  private provider: AIProvider;
  private providerKey: string;

  constructor() {
    this.config = loadConfig();
    this.db = openDatabase(this.config);
    this.memory = new MemoryStore(this.db);
    this.provider = createProvider(this.config);
    this.providerKey = this.config.provider;
  }

  getProvider(): AIProvider {
    if (this.providerKey !== this.config.provider) {
      this.provider = createProvider(this.config);
      this.providerKey = this.config.provider;
      this.completionCache.clear(); // cache invalido ao trocar de cerebro
    }
    return this.provider;
  }

  reloadConfig(cfg: ForgeConfig): void {
    this.config = cfg;
  }
}
