"""Camada de persistência (banco de dados).

Isola todo o acesso ao banco. A memória do agente e os dados do CRM vivem
aqui, de forma CENTRALIZADA e INDEPENDENTE do modelo de IA — trocar Claude
por GPT nunca faz o agente perder histórico, contexto ou dados do cliente.
"""
