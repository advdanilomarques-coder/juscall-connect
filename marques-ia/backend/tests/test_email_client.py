# -*- coding: utf-8 -*-
"""Testa o envio de e-mail via SMTP (app/integrations/email_client.py)."""
from unittest.mock import MagicMock, patch

import pytest

from app.core.config import settings
from app.integrations import email_client
from app.integrations.email_client import EmailError, enviar_email


def _configurar_smtp(monkeypatch):
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.exemplo.com")
    monkeypatch.setattr(settings, "SMTP_PORT", 587)
    monkeypatch.setattr(settings, "SMTP_USER", "envio@exemplo.com")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "senha-app")
    monkeypatch.setattr(settings, "SMTP_FROM_EMAIL", "envio@exemplo.com")
    monkeypatch.setattr(settings, "SMTP_USE_TLS", True)
    monkeypatch.setattr(settings, "SMTP_USE_SSL", False)


def test_envio_desativado_quando_smtp_nao_configurado(monkeypatch):
    monkeypatch.setattr(settings, "SMTP_HOST", "")
    assert enviar_email("cliente@exemplo.com", "Assunto", "Corpo") is False


def test_envio_com_starttls_chama_smtp_e_retorna_true(monkeypatch):
    _configurar_smtp(monkeypatch)

    servidor = MagicMock()
    contexto = MagicMock()
    contexto.__enter__.return_value = servidor
    contexto.__exit__.return_value = False

    with patch.object(email_client.smtplib, "SMTP", return_value=contexto) as mock_smtp:
        ok = enviar_email("cliente@exemplo.com", "Contrato", "Segue em anexo.")

    assert ok is True
    mock_smtp.assert_called_once()
    servidor.starttls.assert_called_once()
    servidor.login.assert_called_once_with("envio@exemplo.com", "senha-app")
    servidor.send_message.assert_called_once()


def test_destino_vazio_levanta_erro(monkeypatch):
    _configurar_smtp(monkeypatch)
    with pytest.raises(EmailError):
        enviar_email("", "Assunto", "Corpo")


def test_falha_de_conexao_vira_email_error(monkeypatch):
    _configurar_smtp(monkeypatch)
    with patch.object(email_client.smtplib, "SMTP", side_effect=OSError("conexão recusada")):
        with pytest.raises(EmailError):
            enviar_email("cliente@exemplo.com", "Assunto", "Corpo")
