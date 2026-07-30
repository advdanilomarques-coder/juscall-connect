"""CRM — gestão de leads, funil (kanban), tarefas e anotações.

Implementa as seções CRM e ETAPAS DO CRM do documento. Toda a lógica de
negócio do funil fica no `service.py`; as rotas HTTP ficam no `router.py`.
O acesso é restrito ao painel administrativo (autenticação JWT).
"""
