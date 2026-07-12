"""Exceções de domínio da aplicação.

Definir exceções próprias (em vez de usar apenas as genéricas do Python)
deixa o tratamento de erros explícito e permite reagir de forma diferente
a cada tipo de falha — essencial para o failover automático da IA.
"""

from __future__ import annotations


class MarquesIAError(Exception):
    """Exceção base — toda exceção do projeto herda desta."""


class AIProviderError(MarquesIAError):
    """Falha ao chamar um provedor de IA específico (timeout, erro de API...).

    Quando o gerenciador de IA captura esta exceção, ele tenta o próximo
    provedor da lista de failover.
    """


class AllProvidersFailedError(MarquesIAError):
    """Todos os provedores de IA falharam — nenhum conseguiu responder."""


class ProviderNotConfiguredError(MarquesIAError):
    """Um provedor foi solicitado mas não tem chave de API configurada."""
