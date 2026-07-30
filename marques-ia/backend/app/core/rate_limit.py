# -*- coding: utf-8 -*-
"""
Rate limiting simples em memória (janela deslizante), usado para proteger o
webhook do WhatsApp e o endpoint de teste do agente contra abuso/spam.

Para múltiplas instâncias do backend rodando em paralelo, isso deveria migrar
para o Redis (já disponível via REDIS_URL) — aqui fica em memória por
simplicidade, adequado para uma única instância.
"""
import time
from collections import defaultdict, deque
from typing import Deque, Dict

_janelas: Dict[str, Deque[float]] = defaultdict(deque)


def permitir(chave: str, limite: int = 20, janela_segundos: int = 60) -> bool:
    """
    Retorna True se a 'chave' (ex.: telefone do cliente, e-mail do admin)
    ainda está dentro do limite de requisições na janela de tempo definida.
    """
    agora = time.time()
    fila = _janelas[chave]

    while fila and agora - fila[0] > janela_segundos:
        fila.popleft()

    if len(fila) >= limite:
        return False

    fila.append(agora)
    return True
