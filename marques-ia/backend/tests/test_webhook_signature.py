# -*- coding: utf-8 -*-
"""Testa a validação HMAC da assinatura do webhook do WhatsApp."""
import hashlib
import hmac

from app.api.routes_whatsapp import _validar_assinatura, settings


def test_assinatura_valida_e_aceita():
    settings.WHATSAPP_APP_SECRET = "segredo-de-teste"
    corpo = b'{"entry": []}'
    assinatura = "sha256=" + hmac.new(b"segredo-de-teste", corpo, hashlib.sha256).hexdigest()

    assert _validar_assinatura(corpo, assinatura) is True


def test_assinatura_invalida_e_rejeitada():
    settings.WHATSAPP_APP_SECRET = "segredo-de-teste"
    corpo = b'{"entry": []}'

    assert _validar_assinatura(corpo, "sha256=assinatura_errada") is False


def test_assinatura_ausente_e_rejeitada():
    settings.WHATSAPP_APP_SECRET = "segredo-de-teste"
    corpo = b'{"entry": []}'

    assert _validar_assinatura(corpo, None) is False


def test_sem_app_secret_configurado_permite_com_aviso():
    settings.WHATSAPP_APP_SECRET = ""
    corpo = b'{"entry": []}'

    assert _validar_assinatura(corpo, None) is True

    # Restaura para não afetar outros testes que rodem depois.
    settings.WHATSAPP_APP_SECRET = "segredo-de-teste"
