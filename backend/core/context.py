# backend/core/context.py
from __future__ import annotations
from typing import Any, Optional
import json

from ..config import settings

def get_current_lang(request: Optional[Any] = None) -> str:
    """
    Retorna o código do idioma atual a partir de settings.LANG_FILE,
    com fallback para settings.DEFAULT_LANG. Tolerante a arquivo ausente/corrompido.
    """
    path = settings.LANG_FILE
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8") or "{}")
            lang = data.get("language")
            if isinstance(lang, str) and lang.strip():
                return lang
    except Exception:
        pass
    return settings.DEFAULT_LANG

def get_current_user(request: Any) -> Optional[str]:
    """
    Retorna o username autenticado da sessão, ou None.
    Mantém compatibilidade com as rotas que só testam truthiness.
    """
    try:
        return request.session.get("username") if hasattr(request, "session") else None
    except Exception:
        return None