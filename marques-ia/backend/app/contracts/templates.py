# -*- coding: utf-8 -*-
"""
Modelos de texto dos contratos gerados automaticamente.

Cada modelo usa placeholders {campo} preenchidos com os dados reais do cliente
e do caso antes da geração do PDF. Placeholders disponíveis:
  {nome_cliente}, {numero_caso}, {resumo_caso}, {data_extenso}, {cidade}

Para trocar por um modelo próprio do escritório, basta editar o texto de
"corpo" do tipo desejado, mantendo os placeholders entre chaves.
"""

_ESCRITORIO = "MARQUES ADVOGADOS ASSOCIADOS"

_FORO = (
    "DO FORO: Fica eleito o foro da comarca de domicílio do(a) CONTRATANTE para dirimir "
    "quaisquer questões oriundas do presente instrumento, com renúncia a qualquer outro, "
    "por mais privilegiado que seja."
)

_ASSINATURA = (
    "E, por estarem assim justos e contratados, firmam o presente instrumento em duas vias "
    "de igual teor e forma.\n\n{cidade}, {data_extenso}."
)

TEMPLATES = {
    "acao_revisional": {
        "titulo": "Contrato de Prestação de Serviços Advocatícios — Ação Revisional",
        "corpo": (
            "Pelo presente instrumento particular de prestação de serviços advocatícios, de um lado "
            "{nome_cliente}, doravante denominado(a) CONTRATANTE, e de outro lado o escritório "
            f"{_ESCRITORIO}, doravante denominado CONTRATADO, têm entre si justo e contratado o seguinte:\n\n"
            "CLÁUSULA 1ª — DO OBJETO: O CONTRATADO prestará ao CONTRATANTE serviços advocatícios "
            "referentes à revisão judicial de cláusulas contratuais e encargos, relativo ao caso nº "
            "{numero_caso}, com o seguinte resumo: \"{resumo_caso}\".\n\n"
            "CLÁUSULA 2ª — DAS OBRIGAÇÕES DO CONTRATADO: Atuar com zelo, diligência e observância das "
            "normas da OAB, mantendo o CONTRATANTE informado sobre o andamento do caso.\n\n"
            "CLÁUSULA 3ª — DAS OBRIGAÇÕES DO CONTRATANTE: Fornecer os documentos e informações "
            "necessários ao regular andamento dos serviços.\n\n"
            "CLÁUSULA 4ª — DOS HONORÁRIOS: Os honorários advocatícios serão definidos em aditivo "
            "específico, observadas as normas e a tabela da OAB.\n\n"
            "CLÁUSULA 5ª — " + _FORO + "\n\n" + _ASSINATURA
        ),
    },
    "busca_e_apreensao": {
        "titulo": "Contrato de Prestação de Serviços Advocatícios — Defesa em Busca e Apreensão",
        "corpo": (
            "Pelo presente instrumento particular, de um lado {nome_cliente}, doravante denominado(a) "
            f"CONTRATANTE, e de outro lado o escritório {_ESCRITORIO}, doravante denominado CONTRATADO, "
            "têm entre si justo e contratado o seguinte:\n\n"
            "CLÁUSULA 1ª — DO OBJETO: Prestação de serviços de defesa técnica em ação de busca e "
            "apreensão de bem financiado, relativo ao caso nº {numero_caso}, com o seguinte resumo: "
            "\"{resumo_caso}\".\n\n"
            "CLÁUSULA 2ª — DAS OBRIGAÇÕES DO CONTRATADO: Promover a defesa dos interesses do "
            "CONTRATANTE com zelo e diligência, observadas as normas da OAB.\n\n"
            "CLÁUSULA 3ª — DAS OBRIGAÇÕES DO CONTRATANTE: Fornecer tempestivamente os documentos e "
            "informações necessários à defesa.\n\n"
            "CLÁUSULA 4ª — DOS HONORÁRIOS: A serem definidos em aditivo específico, observadas as "
            "normas da OAB.\n\n"
            "CLÁUSULA 5ª — " + _FORO + "\n\n" + _ASSINATURA
        ),
    },
    "honorarios": {
        "titulo": "Contrato de Honorários Advocatícios",
        "corpo": (
            "Pelo presente instrumento particular, {nome_cliente} (CONTRATANTE) e o escritório "
            f"{_ESCRITORIO} (CONTRATADO) ajustam os honorários advocatícios referentes ao caso nº "
            "{numero_caso}, com o seguinte resumo: \"{resumo_caso}\".\n\n"
            "CLÁUSULA 1ª — DO OBJETO: Fixação dos honorários advocatícios devidos pela atuação do "
            "CONTRATADO no caso acima identificado.\n\n"
            "CLÁUSULA 2ª — DA FORMA DE PAGAMENTO: Os valores e condições de pagamento serão descritos "
            "em anexo específico a este contrato, observadas as normas da OAB.\n\n"
            "CLÁUSULA 3ª — " + _FORO + "\n\n" + _ASSINATURA
        ),
    },
}

TIPOS_DISPONIVEIS = list(TEMPLATES.keys())
