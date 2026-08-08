import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Logo from "../Logo";
import { api } from "../api";
import { useAuth } from "../auth";

export default function Signup() {
  const { signIn } = useAuth();
  const nav = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError("");
    if (password.length < 6) {
      setError("A senha precisa ter pelo menos 6 caracteres.");
      return;
    }
    setLoading(true);
    try {
      const r = await api.register(email, password, name);
      signIn({ token: r.access_token, email: r.email, displayName: r.display_name });
      nav("/app");
    } catch (err: any) {
      setError(err.message || "Não foi possível criar a conta.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth">
      <div className="aurora" aria-hidden />
      <form className="auth-card" onSubmit={submit} data-reveal>
        <Link to="/" className="brand center"><Logo size={34} /><span>Clean Code</span></Link>
        <h1>Crie sua conta</h1>
        <p className="auth-sub">Grátis para começar. Leva menos de um minuto.</p>

        {error && <div className="alert">{error}</div>}

        <label>Nome</label>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Seu nome" />

        <label>E-mail</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="voce@email.com" required />

        <label>Senha</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="mínimo 6 caracteres" required />

        <button className="btn-primary full" disabled={loading}>
          {loading ? "Criando…" : "Criar conta"}
        </button>

        <p className="auth-alt">
          Já tem conta? <Link to="/login">Entrar</Link>
        </p>
      </form>
    </div>
  );
}
