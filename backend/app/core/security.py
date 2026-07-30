"""Segurança do painel administrativo: hash de senhas e tokens JWT.

Responsabilidades:
  * Guardar senhas SEMPRE em forma de hash (bcrypt) — nunca em texto puro.
  * Emitir e validar tokens JWT usados para autenticar o administrador.

Atende os requisitos de SEGURANÇA do documento do projeto (JWT, controle de
acesso, LGPD). A verificação de token vira uma dependência do FastAPI usada
para proteger as rotas administrativas.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.exceptions import AuthError

# ---------------------------------------------------------------------------
# Hash de senhas — PBKDF2-HMAC-SHA256 (biblioteca padrão do Python).
# ---------------------------------------------------------------------------
# Usamos PBKDF2 (o mesmo algoritmo padrão do Django) por ser um KDF forte,
# lento por design (dificulta força bruta) e SEM dependências externas —
# evitando conflitos de versão entre `passlib` e `bcrypt`. O hash é salgado
# individualmente e a verificação usa comparação em tempo constante.
_PBKDF2_ALGO = "sha256"
_PBKDF2_ITERATIONS = 260_000
_SALT_BYTES = 16


def hash_password(plain: str) -> str:
    """Gera o hash salgado de uma senha no formato

    `pbkdf2_sha256$<iterações>$<salt_hex>$<hash_hex>`.
    """
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGO, plain.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return f"pbkdf2_{_PBKDF2_ALGO}${_PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    """Confere se a senha em texto puro corresponde ao hash armazenado."""
    try:
        algo_label, iterations_str, salt_hex, digest_hex = hashed.split("$")
        algo = algo_label.replace("pbkdf2_", "")
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, AttributeError):
        return False
    candidate = hashlib.pbkdf2_hmac(algo, plain.encode("utf-8"), salt, iterations)
    # Comparação em tempo constante — não vaza informação por timing.
    return hmac.compare_digest(candidate, expected)


def create_access_token(subject: str, *, extra: dict | None = None) -> str:
    """Cria um JWT assinado para o `subject` (ex.: e-mail do admin).

    O token carrega a data de expiração (`exp`) e é assinado com a
    `JWT_SECRET`. Sem a chave correta, ninguém consegue forjar um token.
    """
    now = datetime.now(timezone.utc)
    payload: dict = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Valida e decodifica um JWT. Levanta AuthError se for inválido/expirado."""
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Token expirado.") from exc
    except jwt.PyJWTError as exc:
        raise AuthError("Token inválido.") from exc
