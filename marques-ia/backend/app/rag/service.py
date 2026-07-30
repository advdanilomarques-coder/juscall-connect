# -*- coding: utf-8 -*-
"""Busca os trechos mais relevantes da base de conhecimento para uma consulta."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.knowledge import BaseConhecimento
from app.rag.search import pontuar_relevancia

# Score mínimo para um trecho ser considerado relevante o suficiente para
# entrar no contexto enviado à IA.
LIMIAR_RELEVANCIA_MINIMA = 0.15


def buscar_contexto(
    db: Session,
    consulta: str,
    area_juridica: Optional[str] = None,
    top_k: int = 3,
) -> List[dict]:
    """
    Retorna até `top_k` trechos da base de conhecimento mais relevantes para
    a consulta, opcionalmente filtrados por área jurídica.
    """
    query = db.query(BaseConhecimento)
    if area_juridica:
        query = query.filter(BaseConhecimento.area_juridica == area_juridica)

    documentos = query.all()

    pontuados = [
        (pontuar_relevancia(consulta, f"{doc.titulo} {doc.conteudo}"), doc)
        for doc in documentos
    ]
    relevantes = [(score, doc) for score, doc in pontuados if score >= LIMIAR_RELEVANCIA_MINIMA]
    relevantes.sort(key=lambda item: item[0], reverse=True)

    return [
        {"titulo": doc.titulo, "conteudo": doc.conteudo, "relevancia": round(score, 2)}
        for score, doc in relevantes[:top_k]
    ]
