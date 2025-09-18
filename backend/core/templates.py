# backend/core/templates.py
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional
import json

from fastapi.templating import Jinja2Templates
from fastapi import Request
from jinja2 import pass_context
from markupsafe import Markup, escape

from ..i18n import t as t_i18n
from ..config import settings
from .context import get_current_lang, get_current_user

# Diretório de templates: <raiz>/frontend/templates
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = PROJECT_ROOT / "frontend" / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Jinja: whitespace mais limpo
templates.env.trim_blocks = True
templates.env.lstrip_blocks = True

# -------------------------
# Filtros utilitários
# -------------------------
def _json_filter(value: Any) -> str:
    """Dumps JSON com unicode preservado e indentado."""
    try:
        return json.dumps(value, ensure_ascii=False, indent=2)
    except Exception:
        return json.dumps(str(value), ensure_ascii=False)

def _nl2br(value: Any) -> Markup:
    """Converte quebras de linha em <br>, preservando escape."""
    s = "" if value is None else str(value)
    return Markup("<br>").join(escape(s).splitlines())

templates.env.filters["json"] = _json_filter
templates.env.filters["nl2br"] = _nl2br

# -------------------------
# Helpers globais (Jinja)
# -------------------------
@pass_context
def jinja_t(ctx, key: str, default: Optional[str] = None, lang: Optional[str] = None, **kwargs):
    """
    Tradução dentro do template:
      {{ T('errors.not_found') }}  ou  {{ T('hello', name='Ana') }}
    Aceita lang explícito; caso contrário usa current_lang do contexto.
    """
    cur_lang = lang or ctx.get("current_lang") or settings.DEFAULT_LANG
    val = t_i18n(cur_lang, key, **kwargs)
    if val == key and default is not None:
        return default
    return val

templates.env.globals["T"] = jinja_t
templates.env.globals["settings"] = settings

# -------------------------
# Render helper
# -------------------------
def render_template(
    request: Request,
    template: str,
    context: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
):
    """
    Wrapper para sempre injetar variáveis padrão no contexto.
    Adiciona também um atalho 't' já fixado no idioma corrente.
    """
    context = dict(context or {})

    lang = get_current_lang(request)
    user = get_current_user(request)

    def _t(key: str, **kwargs) -> str:
        return t_i18n(lang, key, **kwargs)

    base_context: Dict[str, Any] = {
        "request": request,
        "current_lang": lang,
        "current_user": user or None,
        "is_authenticated": bool(user),
        "show_footer": True,
        "container_name": None,
        "t": _t,
    }
    base_context.update(context)

    return templates.TemplateResponse(template, base_context, status_code=status_code)