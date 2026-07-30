# -*- coding: utf-8 -*-
"""
Popula a base de conhecimento (RAG) com trechos de referência iniciais para
cada área jurídica atendida — conteúdo genérico de exemplo, que deve ser
revisado e substituído por um advogado antes do uso em produção.
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database.session import Base, SessionLocal, engine  # noqa: E402
from app.models.knowledge import BaseConhecimento  # noqa: E402

TRECHOS_INICIAIS = [
    {
        "area_juridica": "direito_bancario",
        "titulo": "Juros abusivos em contratos bancários",
        "conteudo": (
            "Contratos bancários podem ser revisados judicialmente quando os juros cobrados "
            "excedem significativamente a média de mercado divulgada pelo Banco Central para a "
            "mesma modalidade de operação, configurando onerosidade excessiva. É comum o pedido de "
            "revisão abranger também tarifas cobradas de forma cumulativa ou não informadas "
            "claramente ao consumidor no momento da contratação."
        ),
    },
    {
        "area_juridica": "acao_revisional",
        "titulo": "O que é uma ação revisional de contrato",
        "conteudo": (
            "A ação revisional busca a revisão judicial de cláusulas contratuais consideradas "
            "abusivas ou desproporcionais, comumente em financiamentos de veículos e imóveis. "
            "O processo normalmente envolve perícia contábil para apurar os valores efetivamente "
            "devidos, recalculando o saldo devedor conforme os índices e taxas legalmente aplicáveis."
        ),
    },
    {
        "area_juridica": "busca_e_apreensao",
        "titulo": "Defesa em processos de busca e apreensão",
        "conteudo": (
            "Em processos de busca e apreensão de bens financiados (geralmente veículos), a defesa "
            "pode questionar a regularidade da notificação prévia de mora, o valor cobrado e a "
            "possibilidade de purgação da mora (quitação dos valores em atraso para reaver o bem). "
            "Prazos processuais são curtos, por isso a rapidez no atendimento inicial é importante."
        ),
    },
    {
        "area_juridica": "cnh_area_medica",
        "titulo": "Suspensão de CNH por questões médicas",
        "conteudo": (
            "A suspensão da CNH por resultado de exame médico ou psicológico pode ser contestada "
            "administrativamente junto ao DETRAN, com pedido de nova perícia ou juntada de laudos "
            "médicos complementares. Em alguns casos, cabe também medida judicial para suspender os "
            "efeitos da decisão administrativa até a análise final do recurso."
        ),
    },
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        criados = 0
        for trecho in TRECHOS_INICIAIS:
            existe = (
                db.query(BaseConhecimento)
                .filter(BaseConhecimento.titulo == trecho["titulo"])
                .first()
            )
            if existe:
                continue
            db.add(BaseConhecimento(**trecho))
            criados += 1
        db.commit()
        print(f"Base de conhecimento populada: {criados} trecho(s) novo(s) adicionado(s).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
