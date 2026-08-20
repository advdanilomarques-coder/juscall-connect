import { useEffect, useState } from "react";
import { api, type MemoryItem } from "../api.js";

export function Memory() {
  const [items, setItems] = useState<MemoryItem[]>([]);
  const [q, setQ] = useState("");
  const [value, setValue] = useState("");

  async function refresh() {
    setItems(await api.memory(q));
  }
  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  async function add() {
    if (!value.trim()) return;
    await api.addMemory(value.trim());
    setValue("");
    refresh();
  }
  async function del(id: number) {
    await api.delMemory(id);
    refresh();
  }

  return (
    <div className="panel">
      <div className="panel-inner">
        <h2>Memória</h2>
        <p className="lead">O que o ForgeMind lembra — pesquisável, controlável e apagável. Tudo local.</p>

        <div className="card">
          <div className="field">
            <label>Guardar uma nota / preferência</label>
            <input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && add()}
              placeholder="ex.: prefiro TypeScript com ESM e testes em vitest"
            />
          </div>
          <button className="btn" onClick={add}>Lembrar</button>
        </div>

        <div className="field">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Pesquisar na memória…" />
        </div>

        {items.length === 0 ? (
          <p className="lead">Nenhuma memória ainda.</p>
        ) : (
          items.map((m) => (
            <div className="mem-item" key={m.id}>
              <span className="kind">{m.kind}</span>
              <span className="val">{m.value}</span>
              <button className="del" onClick={() => del(m.id)} title="Apagar">✕</button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
