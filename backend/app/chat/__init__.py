"""Módulo de atendimento (chat) — orquestra a conversa do agente com o cliente.

Reúne a "personalidade" do agente (prompt de sistema), a mensagem inicial
obrigatória e o endpoint HTTP genérico de conversa. Os canais específicos
(WhatsApp, etc.) reutilizam este mesmo núcleo através do serviço de memória.
"""
