import { useEffect, useState } from "react";
import { api, type Config } from "../api.js";

const PROVIDERS: { id: Config["provider"]; name: string; tag: string }[] = [
  { id: "heuristic", name: "Heurístico", tag: "offline • instantâneo • sem modelo" },
  { id: "local-llama", name: "Local Llama", tag: "offline • GGUF • ilimitado" },
  { id: "gemini", name: "Gemini", tag: "online • opcional • requer key" },
];

export function Settings({ onSaved }: { onSaved: () => void }) {
  const [cfg, setCfg] = useState<Config | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getConfig().then(setCfg).catch(() => setCfg(null));
  }, []);

  if (!cfg) return <div className="panel"><div className="panel-inner">Carregando…</div></div>;

  function update<K extends keyof Config>(key: K, value: Config[K]) {
    setCfg((c) => (c ? { ...c, [key]: value } : c));
  }

  async function save() {
    if (!cfg) return;
    setSaving(true);
    try {
      const saved = await api.putConfig({
        provider: cfg.provider,
        theme: cfg.theme,
        port: cfg.port,
        inline: cfg.inline,
        localLlama: cfg.localLlama,
        gemini: cfg.gemini,
      });
      setCfg(saved);
      onSaved();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="panel">
      <div className="panel-inner">
        <h2>Configurações</h2>
        <p className="lead">Tudo fica local em <code>~/.forgemind/config.json</code>. Chaves de API nunca são gravadas aqui.</p>

        <div className="card">
          <h3>Cérebro (provider de IA)</h3>
          <p className="desc">Escolha como o ForgeMind responde. O padrão é offline.</p>
          <div className="provider-pick">
            {PROVIDERS.map((p) => (
              <div
                key={p.id}
                className={`provider-opt ${cfg.provider === p.id ? "active" : ""}`}
                onClick={() => update("provider", p.id)}
              >
                <div className="name">{p.name}</div>
                <div className="tag">{p.tag}</div>
              </div>
            ))}
          </div>
        </div>

        {cfg.provider === "local-llama" && (
          <div className="card">
            <h3>Modelo local (GGUF)</h3>
            <p className="desc">Caminho do modelo baixado. Recomendado: Qwen2.5-3B (Q4) para seu Mac.</p>
            <div className="field">
              <label>Caminho do modelo</label>
              <input
                value={cfg.localLlama.modelPath}
                onChange={(e) => update("localLlama", { ...cfg.localLlama, modelPath: e.target.value })}
                placeholder="./models/qwen2.5-3b-instruct-q4_k_m.gguf"
              />
              <span className="help">Baixe com <code>./scripts/model-pull.sh</code> (uma vez, com internet).</span>
            </div>
            <div className="field">
              <label>Threads de CPU</label>
              <input
                type="number"
                value={cfg.localLlama.threads}
                onChange={(e) => update("localLlama", { ...cfg.localLlama, threads: Number(e.target.value) })}
              />
            </div>
          </div>
        )}

        {cfg.provider === "gemini" && (
          <div className="card">
            <h3>Gemini (online)</h3>
            <p className="desc">A API key fica só no backend, via variável de ambiente <code>GEMINI_API_KEY</code>. Nunca no navegador.</p>
            <div className="field">
              <label>Modelo</label>
              <input value={cfg.gemini.model} onChange={(e) => update("gemini", { model: e.target.value })} />
            </div>
          </div>
        )}

        <div className="card">
          <h3>Aparência & inline</h3>
          <div className="field">
            <label>Tema</label>
            <select value={cfg.theme} onChange={(e) => update("theme", e.target.value as Config["theme"])}>
              <option value="system">Sistema</option>
              <option value="dark">Escuro</option>
              <option value="light">Claro</option>
            </select>
          </div>
          <div className="field">
            <label>Nível do Ghost Text</label>
            <select
              value={cfg.inline.level}
              onChange={(e) => update("inline", { ...cfg.inline, level: e.target.value })}
            >
              <option value="OFF">OFF</option>
              <option value="LOW">LOW</option>
              <option value="BALANCED">BALANCED</option>
              <option value="HIGH">HIGH</option>
            </select>
          </div>
        </div>

        <button className="btn" onClick={save} disabled={saving}>
          {saving ? "Salvando…" : "Salvar configurações"}
        </button>
      </div>
    </div>
  );
}
