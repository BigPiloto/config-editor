# backend/routes/deps.py
from fastapi import HTTPException, status, Request, Header
from ..core.context import get_current_user

__all__ = ["require_user", "browser_blocker"]

def require_user(request: Request):
    """Exige usuário autenticado; lança 401 com chave i18n."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="errors.not_authenticated",
        )
    return user

def browser_blocker(accept: str = Header(default="*/*")):
    """Bloqueia acesso direto via navegador (Accept: text/html)."""
    if "text/html" in (accept or "").lower():
        raise HTTPException(status_code=403, detail="errors.forbidden")
