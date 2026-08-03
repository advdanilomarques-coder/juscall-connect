import { GITHUB_URL, DOCS_URL, MARKETPLACE_URL } from "@/lib/links";

export default function Footer() {
  return (
    <footer className="border-t border-white/5 py-12">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 px-6 sm:flex-row">
        <div className="flex items-center gap-2 font-display font-bold">
          <span className="grid h-7 w-7 place-items-center rounded-md text-ink text-xs"
            style={{ background: "linear-gradient(135deg,#7c3aed,#22d3ee)" }}>
            {"</>"}
          </span>
          Pedro<span className="text-gradient">IA</span>
        </div>
        <nav className="flex gap-6 text-sm text-frost/60">
          <a href={MARKETPLACE_URL} target="_blank" rel="noopener noreferrer" className="hover:text-frost">Download</a>
          <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="hover:text-frost">GitHub</a>
          <a href={DOCS_URL} target="_blank" rel="noopener noreferrer" className="hover:text-frost">Docs</a>
        </nav>
        <p className="text-xs text-frost/40">© {new Date().getFullYear()} PedroIA. Feito com IA.</p>
      </div>
    </footer>
  );
}
