"""Armazenamento físico de arquivos no disco, organizado por cliente/data/tipo.

Estrutura gerada:
    STORAGE_DIR/lead_<id>/<AAAA-MM-DD>/<tipo>/<arquivo>

Isolar o armazenamento aqui permite trocar o backend (disco local hoje, S3
ou Supabase Storage amanhã) sem afetar o resto do sistema — basta manter a
mesma interface `save()`.
"""

from __future__ import annotations

import os
import re
import unicodedata
import uuid
from datetime import datetime, timezone

from app.core.config import settings


def _slugify(value: str) -> str:
    """Normaliza um nome de arquivo (sem acentos, espaços ou caracteres ruins)."""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^\w.\-]+", "_", value).strip("_")
    return value or "arquivo"


def save(lead_id: int, doc_type: str, filename: str, data: bytes) -> tuple[str, int]:
    """Salva os bytes no disco e retorna (caminho_relativo, tamanho_em_bytes).

    Um prefixo aleatório curto evita colisão de nomes se o cliente enviar dois
    arquivos com o mesmo nome no mesmo dia.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    safe_type = _slugify(doc_type)
    safe_name = _slugify(filename)
    directory = os.path.join(
        settings.storage_dir, f"lead_{lead_id}", today, safe_type
    )
    os.makedirs(directory, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    full_path = os.path.join(directory, unique_name)
    with open(full_path, "wb") as fh:
        fh.write(data)

    return full_path, len(data)
