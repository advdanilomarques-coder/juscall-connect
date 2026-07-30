"""Camada de Memória — une persistência (banco) e IA.

Responsável por: recuperar o histórico do cliente, montar o contexto para o
modelo, chamar a camada de IA e salvar a resposta (com metadados de custo).
É aqui que se garante que o agente "continue exatamente de onde a conversa
parou", mesmo após dias ou meses.
"""
