import { useEffect, useState } from "react";
import { api, type Info } from "./api.js";
import { Chat } from "./components/Chat.js";
import { Settings } from "./components/Settings.js";
import { Memory } from "./components/Memory.js";
import { IconChat, IconConfig, IconMemory, IconTheme } from "./components/icons.js";

type Tab = "chat" | "memory" | "config";
type Theme = "system" | "dark" | "light";

export function App() {
  const [tab, setTab] = useState<Tab>("chat");
  const [info, setInfo] = useState<Info | null>(null);
  const [theme, setTheme] = useState<Theme>((localStorage.getItem("fm-theme") as Theme) || "system");
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    api.info().then(setInfo).catch(() => setInfo(null));
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", theme);
    localStorage.setItem("fm-theme", theme);
  }, [theme]);

  function cycleTheme() {
    setTheme((t) => (t === "system" ? "dark" : t === "dark" ? "light" : "system"));
  }

  function showToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(null), 2200);
  }

  const site = info?.site ?? "http://127.0.0.1:4319";

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="mark">◆</div>
          <div>
            <h1>ForgeMind</h1>
            <small>IA local • offline</small>
          </div>
        </div>

        <button className={`nav-btn ${tab === "chat" ? "active" : ""}`} onClick={() => setTab("chat")}>
          <IconChat className="ico" /> Conversa
        </button>
        <button className={`nav-btn ${tab === "memory" ? "active" : ""}`} onClick={() => setTab("memory")}>
          <IconMemory className="ico" /> Memória
        </button>
        <button className={`nav-btn ${tab === "config" ? "active" : ""}`} onClick={() => setTab("config")}>
          <IconConfig className="ico" /> Configurações
        </button>

        <div className="spacer" />

        <div className="side-card">
          <div>
            <span className={`dot ${info?.offline ? "on" : "off"}`} />
            {info ? (info.offline ? "Offline" : "Online") : "Conectando…"}
          </div>
          <div style={{ marginTop: 6 }}>
            provider: <code>{info?.provider ?? "—"}</code>
          </div>
          <div style={{ marginTop: 6 }}>
            site: <code>{site}</code>
          </div>
        </div>
      </aside>

      <main className="main">
        <div className="topbar">
          <div className="title">
            {tab === "chat" ? "Conversa" : tab === "memory" ? "Memória" : "Configurações"}
          </div>
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <span className="badge">{info?.name ?? "ForgeMind"} v{info?.version ?? "0.1.0"}</span>
            <button className="icon-btn" onClick={cycleTheme} title={`Tema: ${theme}`}>
              <IconTheme width={16} height={16} />
            </button>
          </div>
        </div>

        {tab === "chat" && <Chat site={site} />}
        {tab === "memory" && <Memory />}
        {tab === "config" && <Settings onSaved={() => showToast("Configurações salvas")} />}
      </main>

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
