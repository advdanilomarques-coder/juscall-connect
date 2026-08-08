import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Logo from "../Logo";
import { api } from "../api";
import { useAuth } from "../auth";

export default function Login() {
  const { signIn } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const r = await api.login(email, password);
      signIn({ token: r.access_token, email: r.email, displayName: r.display_name });
      nav("/app");
    } catch (err: any) {
      setError(err.message || "Não foi possível entrar.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth">
      <div className="aurora" aria-hidden />
      <form className="auth-card" onSubmit={submit} data-reveal>
        <Link to="/" className="brand center"><Logo size={34} /><span>Clean Code</span></Link>
        <h1>Bem-vindo de volta</h1>
        <p className="auth-sub">Entre para usar o chat e sincronizar suas conversas.</p>

        {error && <div className="alert">{error}</div>}

        <label>E-mail</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="voce@email.com" required />

        <label>Senha</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required />

        <button className="btn-primary full" disabled={loading}>
          {loading ? "Entrando…" : "Entrar"}
        </button>

        <p className="auth-alt">
          Não tem conta? <Link to="/signup">Cadastre-se</Link>
        </p>
      </form>
    </div>
  );
}
