import { createContext, useContext, useEffect, useMemo, useState, ReactNode } from "react";

interface Session {
  token: string;
  email: string;
  displayName: string;
}

interface AuthCtx {
  session: Session | null;
  signIn: (s: Session) => void;
  signOut: () => void;
}

const Ctx = createContext<AuthCtx>({ session: null, signIn: () => {}, signOut: () => {} });
const KEY = "cleancode.session";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      try {
        setSession(JSON.parse(raw));
      } catch {
        localStorage.removeItem(KEY);
      }
    }
  }, []);

  const value = useMemo<AuthCtx>(
    () => ({
      session,
      signIn: (s) => {
        localStorage.setItem(KEY, JSON.stringify(s));
        setSession(s);
      },
      signOut: () => {
        localStorage.removeItem(KEY);
        setSession(null);
      },
    }),
    [session]
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export const useAuth = () => useContext(Ctx);
