# backend/core/totp.py
from __future__ import annotations
import re
from typing import Optional

import pyotp

from ..config import settings

# Parâmetros com fallback (não obrigam definir no config)
_TOTP_INTERVAL = getattr(settings, "TOTP_INTERVAL", 30)
_TOTP_DIGITS = getattr(settings, "TOTP_DIGITS", 6)
_TOTP_WINDOW = getattr(settings, "TOTP_VALID_WINDOW", 1)
_TOTP_ISSUER = getattr(settings, "TOTP_ISSUER", "Config Editor")

def _normalize_code(code: Optional[str]) -> str:
    """Mantém apenas dígitos; preserva zeros à esquerda."""
    if code is None:
        return ""
    return re.sub(r"\D", "", str(code).strip())

def verify_totp(secret: str, code: Optional[str]) -> bool:
    """
    Valida código TOTP.
    - secret: chave base32 salva no user.json
    - code: código informado pelo usuário (com ou sem espaços)
    Retorna True se válido (considerando uma janela de tolerância), senão False.
    """
    if not secret:
        return False

    c = _normalize_code(code)
    if not c:
        return False

    try:
        totp = pyotp.TOTP(secret, interval=_TOTP_INTERVAL, digits=_TOTP_DIGITS)
        return bool(totp.verify(c, valid_window=_TOTP_WINDOW))
    except Exception:
        return False

def generate_totp_uri(secret: str, username: str = "user", issuer: Optional[str] = None) -> str:
    """
    Gera URI para apps TOTP (Google Authenticator, Authy).
    """
    if not secret:
        raise ValueError("errors.invalid_totp_secret")

    name = (username or "user").strip() or "user"
    iss = issuer or _TOTP_ISSUER

    totp = pyotp.TOTP(secret, interval=_TOTP_INTERVAL, digits=_TOTP_DIGITS)
    return totp.provisioning_uri(name=name, issuer_name=iss)

__all__ = ["verify_totp", "generate_totp_uri"]