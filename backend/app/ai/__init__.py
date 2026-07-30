"""Camada de Abstração de IA (AI Provider Layer).

Esta é a peça central da arquitetura descrita no documento do projeto.

Toda comunicação com modelos de IA passa EXCLUSIVAMENTE por esta camada.
As regras de negócio (CRM, atendimento, jurídico) nunca falam diretamente
com Claude, GPT, Gemini ou qualquer outro modelo — elas falam com o
`AIManager`.

Benefícios (Princípio da Inversão de Dependência — o "D" do SOLID):
  * Trocar/adicionar modelos = criar um novo Provider, sem tocar no resto.
  * Failover automático entre modelos, com retry e backoff.
  * Roteamento inteligente por tipo de tarefa.
  * Controle de custos (tokens/valor) centralizado.
  * Memória e regras de negócio ficam independentes do modelo de IA.
"""
