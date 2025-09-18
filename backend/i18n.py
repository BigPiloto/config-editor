# backend/i18n.py
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Tuple
import json
import threading

from .config import settings

# /backend/locales
LOCALES_DIR = Path(__file__).resolve().parent / "locales"

# cache por arquivo: { Path: (mtime, data_dict) }
_CACHE: Dict[Path, Tuple[float, Dict[str, Any]]] = {}
_LOCK = threading.Lock()

def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    mtime = path.stat().st_mtime
    with _LOCK:
        cached = _CACHE.get(path)
        if cached and cached[0] == mtime:
            return cached[1]
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
    except Exception:
        data = {}
    with _LOCK:
        _CACHE[path] = (mtime, data)
    return data

def _lang_path(lang: str) -> Path:
    return LOCALES_DIR / f"{lang}.json"

def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merge profundo: override vence; não muta os originais."""
    out: Dict[str, Any] = {}
    for k in base.keys() | override.keys():
        bv = base.get(k)
        ov = override.get(k)
        if isinstance(bv, dict) and isinstance(ov, dict):
            out[k] = _deep_merge(bv, ov)
        elif ov is not None:
            out[k] = ov
        else:
            out[k] = bv
    return out

def load_locale(lang: str | None) -> Dict[str, Any]:
    """Carrega o dicionário do idioma solicitado, com fallback profundo para settings.DEFAULT_LANG."""
    req = lang or settings.DEFAULT_LANG
    default_data = _read_json(_lang_path(settings.DEFAULT_LANG))
    if req == settings.DEFAULT_LANG:
        return default_data
    req_data = _read_json(_lang_path(req))
    if not req_data:
        return default_data
    return _deep_merge(default_data, req_data)

def resolve_key(data: dict, key: str) -> str:
    """Navega no dicionário por chave pontilhada; se faltar, devolve a própria key."""
    cur: Any = data
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return key
    return cur if isinstance(cur, str) else key

class _SafeFmt(dict):
    def __missing__(self, k):
        return "{" + k + "}"

def t(lang: str | None, key: str, **kwargs) -> str:
    """
    Retorna a tradução da chave:
      1) idioma solicitado (com fallback profundo ao default);
      2) se faltar, devolve a própria key.
    Suporta interpolação: t(lang, "greet", name="Ana")
    """
    val = resolve_key(load_locale(lang), key)
    if kwargs and isinstance(val, str):
        try:
            # tolerante a placeholders ausentes
            val = val.format_map(_SafeFmt(kwargs))
        except Exception:
            pass
    return val

def clear_i18n_cache() -> None:
    """Limpa o cache de traduções (força releitura dos arquivos no próximo acesso)."""
    with _LOCK:
        _CACHE.clear()

def available_langs() -> list[str]:
    """Lista os códigos de idioma disponíveis em backend/locales (ex.: ['en', 'pt-BR'])."""
    return sorted(p.stem for p in LOCALES_DIR.glob("*.json") if p.is_file())
