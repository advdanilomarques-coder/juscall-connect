"""System prompts and slash-command expansion — the 'engineer persona' of PedroIA."""
from typing import Dict, Optional

SYSTEM_PROMPT = (
    "Você é o PedroIA, um engenheiro de software sênior integrado ao VS Code. "
    "Você domina Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, PHP, Kotlin e Swift, "
    "além de frontend (React, Vue, Angular, Tailwind), backend (REST, GraphQL, microserviços, "
    "arquitetura limpa, segurança) e bancos de dados (PostgreSQL, MySQL, MongoDB, Redis, SQLite). "
    "Responda de forma objetiva e profissional, em português. "
    "Quando gerar código, use blocos de código com a linguagem correta e explique brevemente. "
    "Prefira soluções idiomáticas, seguras e prontas para produção."
)

# Slash command -> extra guidance appended to the system prompt.
SLASH_COMMANDS: Dict[str, str] = {
    "/create": "O usuário quer CRIAR algo novo. Proponha a estrutura de pastas/arquivos e o código completo de cada arquivo.",
    "/criar": "O usuário quer CRIAR algo novo. Proponha a estrutura de pastas/arquivos e o código completo de cada arquivo.",
    "/explain": "Explique o código de forma clara, cobrindo o que faz, como e por quê.",
    "/fix": "Encontre e corrija os erros. Mostre o diff/correção e explique a causa raiz.",
    "/corrigir": "Encontre e corrija os erros. Mostre o diff/correção e explique a causa raiz.",
    "/refactor": "Refatore melhorando legibilidade, desempenho e manutenção, preservando o comportamento.",
    "/melhorar": "Refatore melhorando legibilidade, desempenho e manutenção, preservando o comportamento.",
    "/test": "Gere testes automatizados cobrindo casos felizes e de borda, usando o framework idiomático.",
    "/security": "Faça uma análise de segurança: liste vulnerabilidades, severidade e correções recomendadas.",
}


def detect_slash(text: str) -> Optional[str]:
    stripped = text.lstrip()
    for cmd in SLASH_COMMANDS:
        if stripped.lower().startswith(cmd):
            return cmd
    return None


def build_system_prompt(user_text: str, context_block: str = "") -> str:
    parts = [SYSTEM_PROMPT]
    cmd = detect_slash(user_text)
    if cmd:
        parts.append(SLASH_COMMANDS[cmd])
    if context_block:
        parts.append("Contexto do projeto (fornecido automaticamente pelo editor):\n" + context_block)
    return "\n\n".join(parts)


def format_context(ctx: Optional[dict]) -> str:
    if not ctx:
        return ""
    lines = []
    if ctx.get("workspace_name"):
        lines.append(f"Workspace: {ctx['workspace_name']}")
    if ctx.get("file_path"):
        lines.append(f"Arquivo ativo: {ctx['file_path']} ({ctx.get('language', '?')})")
    if ctx.get("open_files"):
        lines.append("Arquivos abertos: " + ", ".join(ctx["open_files"][:15]))
    if ctx.get("diagnostics"):
        lines.append("Diagnósticos (erros/avisos):\n" + "\n".join(ctx["diagnostics"][:20]))
    if ctx.get("selection"):
        sel = ctx["selection"]
        lines.append("Seleção atual:\n```\n" + sel[:2000] + "\n```")
    return "\n".join(lines)
