# -*- coding: utf-8 -*-
"""
Prompt de sistema do agente jurídico e montagem da lista de mensagens
enviada ao provedor de IA — incluindo a distinção entre cliente novo e
cliente antigo (recorrente), e o contexto trazido pelo RAG (seção 14).
"""
from typing import List, Optional

SYSTEM_PROMPT = """Você é o atendimento do escritório Marques Advogados Associados,
especializado em Direito Bancário, Ação Revisional, Busca e Apreensão e questões de
CNH na área médica.

Regras obrigatórias e invioláveis:
- Fale sempre em nome do escritório. Nunca revele que é uma inteligência artificial.
- Nunca prometa resultado, vitória em processo ou valor de indenização.
- Use linguagem profissional, clara, objetiva e acolhedora.
- Lembre e utilize o nome do cliente quando ele estiver disponível no histórico.
- Colete apenas os dados estritamente necessários para a triagem do caso.
- Se o assunto fugir das áreas atendidas, envolver urgência, ou o cliente pedir
  atendimento humano, informe que um advogado dará continuidade e sinalize isso
  claramente na resposta.
- Baseie-se apenas no contexto e no histórico fornecidos nesta conversa.
- O agente deve atender TODOS os clientes: tanto quem fala com o escritório pela
  primeira vez quanto quem já conversou antes. Nunca ignore ou trate de forma
  genérica um cliente recorrente — use sempre o histórico disponível.
"""

INSTRUCAO_CLIENTE_NOVO = (
    "Este é o PRIMEIRO contato deste cliente com o escritório (cliente novo). "
    "Dê boas-vindas profissionais, apresente brevemente o escritório e inicie a "
    "triagem coletando apenas nome completo e um resumo do caso."
)

INSTRUCAO_CLIENTE_ANTIGO = (
    "Este é um cliente que JÁ conversou com o escritório antes (cliente recorrente). "
    "Não se apresente novamente nem repita a saudação institucional completa. "
    "Continue a conversa com naturalidade, usando o histórico abaixo como contexto "
    "e retomando exatamente de onde a conversa parou."
)


def build_messages(
    history: List[dict],
    user_message: str,
    client_name: Optional[str] = None,
    cliente_novo: bool = True,
    contexto_rag: Optional[List[dict]] = None,
) -> List[dict]:
    """
    Monta a lista de mensagens no formato esperado pela API de chat do
    OpenRouter (compatível com o formato da OpenAI: {"role": ..., "content": ...}).

    cliente_novo=True  -> cliente sem histórico prévio (primeiro contato)
    cliente_novo=False -> cliente recorrente (já existe histórico salvo)
    contexto_rag        -> trechos da base de conhecimento jurídica (seção 14),
                           já filtrados e ranqueados por relevância
    """
    messages: List[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    messages.append({
        "role": "system",
        "content": INSTRUCAO_CLIENTE_NOVO if cliente_novo else INSTRUCAO_CLIENTE_ANTIGO,
    })

    if client_name:
        messages.append({
            "role": "system",
            "content": f"O nome do cliente nesta conversa é: {client_name}.",
        })

    if contexto_rag:
        texto_contexto = "\n\n".join(
            f"[{trecho['titulo']}]\n{trecho['conteudo']}" for trecho in contexto_rag
        )
        messages.append({
            "role": "system",
            "content": (
                "Use as informações de referência abaixo, quando forem relevantes, para "
                "fundamentar sua resposta. Não cite estas fontes explicitamente ao cliente "
                "nem mencione que consultou uma base de conhecimento:\n\n" + texto_contexto
            ),
        })

    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages
