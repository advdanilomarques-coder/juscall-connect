"""Canais de atendimento — abstração multicanal.

O agente deve funcionar em vários canais (WhatsApp, Instagram, Telegram,
site...). Toda a lógica de conversa é única (memory_service); cada canal só
precisa: (1) receber a mensagem e normalizá-la, e (2) enviar a resposta de
volta no formato do canal.

Adicionar um canal novo = criar um cliente que implemente `ChannelClient`,
sem tocar na lógica de atendimento (Aberto/Fechado).
"""
