// @ts-check
(function () {
  const vscode = acquireVsCodeApi();
  const messagesEl = document.getElementById("messages");
  const inputEl = /** @type {HTMLTextAreaElement} */ (document.getElementById("input"));
  const sendEl = document.getElementById("send");
  const modeEl = /** @type {HTMLSelectElement} */ (document.getElementById("mode"));
  const statusEl = document.getElementById("statusBar");

  let thinkingEl = null;

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );
  }

  // Minimal, safe markdown: fenced code blocks + inline code. Everything else escaped.
  function renderMarkdown(text) {
    const parts = text.split(/```/);
    let html = "";
    for (let i = 0; i < parts.length; i++) {
      if (i % 2 === 1) {
        const body = parts[i].replace(/^[a-zA-Z0-9_+-]*\n/, "");
        html += `<pre><code>${escapeHtml(body)}</code></pre>`;
      } else {
        let seg = escapeHtml(parts[i]);
        seg = seg.replace(/`([^`]+)`/g, "<code>$1</code>");
        html += seg;
      }
    }
    return html;
  }

  function addMessage(role, text, meta) {
    removeThinking();
    const el = document.createElement("div");
    el.className = "msg " + role;
    el.innerHTML = renderMarkdown(text);
    if (meta) {
      const m = document.createElement("span");
      m.className = "meta";
      m.textContent = meta;
      el.appendChild(m);
    }
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function showThinking() {
    removeThinking();
    thinkingEl = document.createElement("div");
    thinkingEl.className = "thinking";
    thinkingEl.textContent = "PedroIA está pensando…";
    messagesEl.appendChild(thinkingEl);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function removeThinking() {
    if (thinkingEl && thinkingEl.parentNode) {
      thinkingEl.parentNode.removeChild(thinkingEl);
    }
    thinkingEl = null;
  }

  function send() {
    const text = inputEl.value.trim();
    if (!text) return;
    addMessage("user", text);
    inputEl.value = "";
    inputEl.style.height = "auto";
    vscode.postMessage({ type: "sendMessage", text, mode: modeEl.value });
  }

  sendEl.addEventListener("click", send);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });
  inputEl.addEventListener("input", () => {
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + "px";
  });

  window.addEventListener("message", (event) => {
    const msg = event.data;
    switch (msg.type) {
      case "assistant":
        addMessage("assistant", msg.text, msg.meta);
        break;
      case "userEcho":
        addMessage("user", msg.text);
        break;
      case "prefill":
        inputEl.value = msg.text;
        inputEl.style.height = "auto";
        inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + "px";
        inputEl.focus();
        inputEl.scrollTop = inputEl.scrollHeight;
        break;
      case "thinking":
        showThinking();
        break;
      case "error":
        addMessage("error", "⚠️ " + msg.text);
        break;
      case "status":
        statusEl.textContent = msg.text;
        statusEl.className = "status " + (msg.ok ? "ok" : "bad");
        break;
    }
  });

  vscode.postMessage({ type: "ready" });
})();
