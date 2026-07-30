# -*- coding: utf-8 -*-
"""Testa a pontuação de relevância e a busca de contexto do RAG."""
from app.models.knowledge import BaseConhecimento
from app.rag.search import pontuar_relevancia
from app.rag.service import buscar_contexto


def test_documento_relevante_pontua_mais_que_irrelevante():
    consulta = "juros abusivos no meu financiamento de carro"
    doc_relevante = "Juros abusivos em contratos bancários podem ser revisados quando excedem a média de mercado."
    doc_irrelevante = "Suspensão de CNH por questões médicas pode ser contestada junto ao DETRAN."

    score_relevante = pontuar_relevancia(consulta, doc_relevante)
    score_irrelevante = pontuar_relevancia(consulta, doc_irrelevante)

    assert score_relevante > score_irrelevante
    assert score_relevante > 0


def test_buscar_contexto_retorna_apenas_documentos_acima_do_limiar(db_session):
    db_session.add(BaseConhecimento(
        area_juridica="direito_bancario",
        titulo="Juros abusivos em contratos bancários",
        conteudo="Contratos bancários com juros muito acima da média de mercado podem ser revisados judicialmente.",
    ))
    db_session.add(BaseConhecimento(
        area_juridica="cnh_area_medica",
        titulo="Suspensão de CNH",
        conteudo="A suspensão da CNH por exame médico pode ser contestada administrativamente no DETRAN.",
    ))
    db_session.commit()

    resultados = buscar_contexto(db_session, consulta="meu contrato bancário tem juros abusivos", top_k=3)

    assert len(resultados) >= 1
    assert any("Juros abusivos" in r["titulo"] for r in resultados)


def test_buscar_contexto_filtra_por_area_juridica(db_session):
    db_session.add(BaseConhecimento(
        area_juridica="direito_bancario", titulo="Doc Bancário", conteudo="juros abusivos contrato bancário",
    ))
    db_session.add(BaseConhecimento(
        area_juridica="cnh_area_medica", titulo="Doc CNH", conteudo="juros abusivos não tem nada a ver com CNH",
    ))
    db_session.commit()

    resultados = buscar_contexto(
        db_session, consulta="juros abusivos", area_juridica="direito_bancario", top_k=5,
    )

    assert all(r["titulo"] == "Doc Bancário" for r in resultados)
