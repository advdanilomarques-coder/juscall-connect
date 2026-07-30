"""Rate limiting simples em memória (token bucket por IP).

Protege a API pública contra abuso e picos de requisições, atendendo o
requisito de SEGURANÇA (Rate Limit) do documento do projeto.

Implementação em memória (sem Redis) para funcionar em qualquer ambiente,
inclusive local sem Docker. Em produção com múltiplas instâncias, troque
por um limitador distribuído (Redis) — a interface `allow()` permanece igual,
então nenhum outro código precisa mudar (baixo acoplamento).
"""

from __future__ import annotations

import time
from collections import defaultdict


class InMemoryRateLimiter:
    """Limita requisições por chave (ex.: IP) numa janela deslizante de 60s."""

    def __init__(self, per_minute: int) -> None:
        self._per_minute = per_minute
        self._hits: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str) -> bool:
        """Retorna True se a requisição está dentro do limite; False se estourou."""
        if self._per_minute <= 0:
            return True  # limite desativado
        now = time.monotonic()
        window_start = now - 60.0
        hits = self._hits[key]
        # Descarta os registros mais antigos que a janela de 60s.
        hits[:] = [t for t in hits if t >= window_start]
        if len(hits) >= self._per_minute:
            return False
        hits.append(now)
        return True
