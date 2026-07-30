"""Modelos (templates) de contrato em texto, com marcadores de preenchimento.

Cada modelo é uma lista de parágrafos com placeholders no estilo `{campo}`.
Manter os textos aqui (separados da geração de PDF) permite ao escritório
editar o conteúdo jurídico sem mexer no código de renderização.

Placeholders disponíveis:
  {nome} {cpf} {rg} {endereco} {telefone} {email} {objeto} {honorarios}
  {data} {cidade} {advogado} {oab}
"""

from __future__ import annotations

# Modelo padrão: contrato de honorários advocatícios.
HONORARIOS: dict = {
    "titulo": "CONTRATO DE PRESTAÇÃO DE SERVIÇOS ADVOCATÍCIOS",
    "paragrafos": [
        "CONTRATANTE: {nome}, inscrito(a) no CPF sob o nº {cpf}, RG nº {rg}, "
        "residente e domiciliado(a) em {endereco}, telefone {telefone}, "
        "e-mail {email}.",
        "CONTRATADO(A): {advogado}, advogado(a) inscrito(a) na {oab}, doravante "
        "denominado(a) simplesmente CONTRATADO(A).",
        "CLÁUSULA 1ª — DO OBJETO. O presente contrato tem por objeto a "
        "prestação de serviços advocatícios referentes a: {objeto}.",
        "CLÁUSULA 2ª — DOS HONORÁRIOS. Pelos serviços prestados, o(a) "
        "CONTRATANTE pagará ao(à) CONTRATADO(A) os honorários assim ajustados: "
        "{honorarios}.",
        "CLÁUSULA 3ª — DAS OBRIGAÇÕES. O(A) CONTRATADO(A) obriga-se a conduzir "
        "a causa com zelo e diligência, mantendo o(a) CONTRATANTE informado(a) "
        "sobre o andamento do processo.",
        "CLÁUSULA 4ª — DO FORO. Fica eleito o foro da comarca de {cidade} para "
        "dirimir quaisquer dúvidas oriundas deste contrato.",
        "E, por estarem assim justos e contratados, firmam o presente "
        "instrumento em duas vias de igual teor e forma.",
        "{cidade}, {data}.",
    ],
    "assinaturas": [
        "_______________________________\n{nome} (CONTRATANTE)",
        "_______________________________\n{advogado} — {oab} (CONTRATADO/A)",
    ],
}

# Registro de modelos disponíveis (adicionar novos = incluir aqui).
TEMPLATES: dict[str, dict] = {
    "honorarios": HONORARIOS,
}


def get_template(name: str) -> dict:
    """Retorna o modelo pelo nome; cai no padrão 'honorarios' se não existir."""
    return TEMPLATES.get(name, HONORARIOS)
