# -*- coding: utf-8 -*-
"""
Pontuação de relevância texto a texto por sobreposição de palavras-chave.

Deliberadamente NÃO usa embeddings de terceiros (ex.: API de embeddings) para
manter o requisito de uma única chave de API no projeto — a busca semântica
"de verdade" com ChromaDB/FAISS pode substituir este módulo no futuro sem
mudar a interface pública (buscar_contexto).
"""
import re
from collections import Counter
from typing import List

_PALAVRAS_IRRELEVANTES = {
    "de", "a", "o", "que", "e", "do", "da", "em", "um", "uma", "para", "com",
    "não", "os", "as", "se", "na", "por", "mais", "as", "dos", "como", "mas",
    "ao", "ele", "das", "seu", "sua", "ou", "quando", "muito", "nos", "já",
    "eu", "também", "só", "pelo", "pela", "até", "isso", "ela", "entre",
    "depois", "sem", "mesmo", "aos", "seus", "quem", "nas", "me", "esse",
    "eles", "você", "essa", "num", "nem", "suas", "meu", "às", "minha",
}


def _tokenizar(texto: str) -> List[str]:
    palavras = re.findall(r"[a-zà-úçã]+", texto.lower())
    return [p for p in palavras if p not in _PALAVRAS_IRRELEVANTES and len(p) > 2]


def pontuar_relevancia(consulta: str, conteudo: str) -> float:
    """
    Retorna um score entre 0 e 1 representando o quanto do vocabulário da
    consulta aparece no conteúdo (proporção de tokens da consulta cobertos).
    """
    tokens_consulta = Counter(_tokenizar(consulta))
    tokens_conteudo = Counter(_tokenizar(conteudo))

    if not tokens_consulta:
        return 0.0

    intersecao = sum(min(qtd, tokens_conteudo[palavra]) for palavra, qtd in tokens_consulta.items())
    return intersecao / sum(tokens_consulta.values())
