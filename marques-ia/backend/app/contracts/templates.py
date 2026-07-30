# -*- coding: utf-8 -*-
"""
Modelos de texto dos contratos/documentos gerados automaticamente.
Cada modelo usa placeholders no formato {campo}, preenchidos com os dados
reais do cliente e do caso antes da geração do PDF.
"""

TEMPLATES = {
    "acao_revisional": {
        "titulo": "Contrato de Prestação de Serviços Advocatícios — Ação Revisional",
        "corpo": (
            "Pelo presente instrumento particular, de um lado {nome_cliente}, doravante denominado(a) "
            "CONTRATANTE, e de outro lado Marques Advogados Associados, doravante denominado CONTRATADO, "
            "têm entre si justo e contratado o seguinte:\n\n"
            "1. OBJETO: prestação de serviços advocatícios para revisão judicial de cláusulas contratuais "
            "referentes ao caso nº {numero_caso}, com resumo: \"{resumo_caso}\".\n\n"
            "2. HONORÁRIOS: a serem definidos em aditivo específico, observadas as normas da OAB.\n\n"
            "3. OBRIGAÇÕES: o CONTRATADO se compromete a atuar com zelo e diligência na condução do caso, "
            "mantendo o CONTRATANTE informado sobre o andamento processual.\n\n"
            "4. FORO: fica eleito o foro da comarca do CONTRATANTE para dirimir quaisquer dúvidas "
            "oriundas deste contrato."
        ),
    },
    "busca_e_apreensao": {
        "titulo": "Contrato de Prestação de Serviços Advocatícios — Defesa em Busca e Apreensão",
        "corpo": (
            "Pelo presente instrumento particular, {nome_cliente} (CONTRATANTE) contrata Marques Advogados "
            "Associados (CONTRATADO) para atuar na defesa referente ao caso nº {numero_caso}, com resumo: "
            "\"{resumo_caso}\".\n\n"
            "1. OBJETO: defesa técnica em processo de busca e apreensão de bem financiado.\n\n"
            "2. HONORÁRIOS: a serem definidos em aditivo específico, observadas as normas da OAB.\n\n"
            "3. FORO: fica eleito o foro da comarca do CONTRATANTE."
        ),
    },
    "honorarios": {
        "titulo": "Contrato de Honorários Advocatícios",
        "corpo": (
            "{nome_cliente} (CONTRATANTE) e Marques Advogados Associados (CONTRATADO) ajustam os "
            "honorários referentes ao caso nº {numero_caso} (\"{resumo_caso}\"), a serem pagos conforme "
            "condições descritas em anexo específico a este contrato."
        ),
    },
}

TIPOS_DISPONIVEIS = list(TEMPLATES.keys())
