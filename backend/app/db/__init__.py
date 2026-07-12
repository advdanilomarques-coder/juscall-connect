"""Camada de persistência (banco de dados).

Isola todo o acesso ao banco. A memória do agente vive aqui, de forma
CENTRALIZADA e INDEPENDENTE do modelo de IA — trocar Claude por GPT nunca
faz o agente perder histórico, contexto ou dados do cliente.
"""
