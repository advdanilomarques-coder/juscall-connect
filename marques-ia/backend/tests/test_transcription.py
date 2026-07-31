# -*- coding: utf-8 -*-
"""Testa a transcrição de áudio (app/integrations/transcription.py)."""
import asyncio

import pytest

from app.core.config import settings
from app.integrations.transcription import TranscricaoError, transcrever_audio


def test_transcricao_desativada_levanta_erro(monkeypatch):
    """Sem TRANSCRICAO_API_KEY, deve levantar TranscricaoError (o webhook trata pedindo texto)."""
    monkeypatch.setattr(settings, "TRANSCRICAO_API_KEY", "")
    with pytest.raises(TranscricaoError):
        asyncio.run(transcrever_audio(b"audio-falso"))


def test_transcricao_habilitada_flag(monkeypatch):
    monkeypatch.setattr(settings, "TRANSCRICAO_API_KEY", "")
    assert settings.TRANSCRICAO_HABILITADA is False
    monkeypatch.setattr(settings, "TRANSCRICAO_API_KEY", "chave-teste")
    assert settings.TRANSCRICAO_HABILITADA is True
