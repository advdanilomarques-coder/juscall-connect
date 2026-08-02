# -*- coding: utf-8 -*-
"""
Modelos de texto dos contratos gerados automaticamente.

Cada modelo usa placeholders {campo} preenchidos com os dados reais do cliente
e do caso antes da geração do PDF. Placeholders disponíveis:
  {nome_cliente}, {numero_caso}, {resumo_caso}, {data_extenso}, {cidade}

Para trocar por um modelo próprio do escritório, basta editar o texto de
"corpo" do tipo desejado, mantendo os placeholders entre chaves.
"""

_ESCRITORIO = "MARQUES ADVOCACIA"

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
    "direito_bancario": {
        "titulo": "Contrato de Prestação de Serviços Advocatícios — Direito Bancário",
        "corpo": (
            "CONTRATANTE: {nome_cliente}, [nacionalidade], [estado civil], [profissão], portador(a) do "
            "RG nº [_____] e inscrito(a) no CPF/CNPJ sob o nº [_____], residente e domiciliado(a) / com "
            "sede em [endereço completo, cidade/UF, CEP], doravante denominado(a) simplesmente CONTRATANTE;\n\n"
            "CONTRATADO: MARQUES ADVOCACIA, sociedade individual de advocacia representada por Danilo "
            "Barbosa Marques, brasileiro, advogado, inscrito na OAB/SP sob o nº 467.790, com escritório "
            "profissional na Rua Joseph Zarour, nº 93, Sala 1805, Centro, Guarulhos/SP, doravante "
            "denominado simplesmente CONTRATADO;\n\n"
            "Têm entre si justo e contratado o presente instrumento particular de prestação de serviços "
            "advocatícios, que se regerá pelas cláusulas e condições seguintes, bem como pela Lei nº "
            "8.906/1994 (Estatuto da OAB) e pelo Código de Ética e Disciplina da OAB.\n\n"
            "Referência do caso: nº {numero_caso} — \"{resumo_caso}\".\n\n"
            "CLÁUSULA 1ª – DO OBJETO: O presente contrato tem por objeto a prestação de serviços "
            "advocatícios pelo CONTRATADO ao CONTRATANTE, em caráter de mandato judicial e extrajudicial, "
            "especificamente relacionados a questões de Direito Bancário e do Consumidor, compreendendo, "
            "dentre outras: a) Ação Revisional de Contrato Bancário/Financiamento (encargos, juros "
            "remuneratórios, capitalização, tarifas e cláusulas abusivas); b) Defesa em Ação de Busca e "
            "Apreensão por alienação fiduciária (Decreto-Lei nº 911/1969), incluindo contestação, purgação "
            "de mora e recursos; c) Ações de Consignação em Pagamento e Depósito; d) Ações Declaratórias "
            "de Inexistência de Débito, Repetição de Indébito e Indenização por Danos Morais/Materiais; "
            "e) Impugnações e defesas em Cumprimento de Sentença, Execuções e bloqueios via SISBAJUD; "
            "f) Negociação e composição extrajudicial de dívidas bancárias; g) demais medidas correlatas "
            "no âmbito bancário/financeiro, mediante prévio ajuste. A atuação limita-se ao(s) processo(s) "
            "indicado(s) no Anexo I ou em procuração específica, salvo aditamento.\n\n"
            "CLÁUSULA 2ª – DOS HONORÁRIOS: Pelos serviços, o CONTRATANTE pagará honorários contratuais "
            "fixos de R$ [_____] ([valor por extenso]), na forma [à vista / parcelado em ___ vezes de "
            "R$ ___]. Fica ajustado honorário de êxito de [___]% sobre o proveito econômico efetivamente "
            "obtido (sentença favorável, acordo, compensação, redução de débito ou outro benefício "
            "patrimonial). Os honorários de sucumbência pertencem exclusivamente ao CONTRATADO (art. 23 da "
            "Lei nº 8.906/1994). O atraso sujeita o CONTRATANTE a multa de 2%, juros de mora de 1% ao mês "
            "e correção pelo índice [INPC/IPCA].\n\n"
            "CLÁUSULA 3ª – DAS DESPESAS PROCESSUAIS: Custas, taxas, emolumentos, diligências, perícias e "
            "demais despesas correm por conta exclusiva do CONTRATANTE, cobradas em separado dos honorários "
            "da Cláusula 2ª, mediante prévio orçamento ou comprovação.\n\n"
            "CLÁUSULA 4ª – DAS OBRIGAÇÕES DO CONTRATADO: empregar diligência e técnica na defesa dos "
            "interesses do CONTRATANTE, observada a ética da OAB; manter o CONTRATANTE informado do "
            "andamento; guardar sigilo profissional (art. 34, VII, da Lei nº 8.906/1994); praticar os atos "
            "nos prazos legais; e prestar contas de valores recebidos em nome do CONTRATANTE.\n\n"
            "CLÁUSULA 5ª – DAS OBRIGAÇÕES DO CONTRATANTE: fornecer com veracidade os documentos e "
            "informações necessários; pagar honorários e despesas nos prazos; comunicar alterações de "
            "contato ou fatos relevantes; não transigir ou confessar dívida sem ciência do CONTRATADO; e "
            "outorgar as procurações necessárias.\n\n"
            "CLÁUSULA 6ª – DO PRAZO: vigora da assinatura até o encerramento definitivo do(s) processo(s), "
            "incluindo recursos e cumprimento de sentença, salvo rescisão antecipada.\n\n"
            "CLÁUSULA 7ª – DA RESCISÃO E RENÚNCIA/REVOGAÇÃO: pode ser rescindido por qualquer parte mediante "
            "aviso escrito com [___] dias de antecedência. Na revogação sem justa causa, são devidos "
            "honorários proporcionais aos serviços prestados. Na renúncia, observa-se o prazo do art. 5º, "
            "§3º, do Estatuto da OAB.\n\n"
            "CLÁUSULA 8ª – DO SIGILO E DA LGPD: o CONTRATADO mantém sigilo sobre os dados do CONTRATANTE, "
            "usados apenas para a prestação dos serviços, conforme a Lei nº 13.709/2018 (LGPD), podendo "
            "compartilhá-los com o Judiciário e terceiros estritamente necessários ao andamento da causa.\n\n"
            "CLÁUSULA 9ª – DO SUBSTABELECIMENTO: fica autorizado o substabelecimento, com ou sem reserva de "
            "poderes, a outro(s) advogado(s) inscrito(s) na OAB, permanecendo o CONTRATADO responsável pela "
            "condução da causa.\n\n"
            "CLÁUSULA 10ª – DA AUSÊNCIA DE GARANTIA DE RESULTADO: a atividade advocatícia é obrigação de "
            "meio, e não de resultado; o CONTRATADO não garante o êxito da demanda, comprometendo-se a "
            "empregar todos os esforços técnicos cabíveis.\n\n"
            "CLÁUSULA 11ª – DO FORO: fica eleito o foro da Comarca de Guarulhos/SP para dirimir dúvidas "
            "oriundas deste contrato, com renúncia a qualquer outro.\n\n"
            "CLÁUSULA 12ª – DISPOSIÇÕES GERAIS: o instrumento obriga as partes e sucessores; a tolerância "
            "quanto a descumprimento não implica novação; firmado em caráter irrevogável e irretratável, "
            "salvo hipóteses aqui previstas.\n\n"
            "E, por estarem assim justas e contratadas, as partes assinam o presente instrumento em 2 (duas) "
            "vias de igual teor e forma, na presença das testemunhas abaixo.\n\n"
            "{cidade}, {data_extenso}."
        ),
    },
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
