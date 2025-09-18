# backend/routes/main.py
from fastapi import APIRouter, Request, HTTPException, status, Header
from fastapi.responses import RedirectResponse
import json
from pydantic import BaseModel

from ..core.templates import render_template
from ..core.context import get_current_user
from ..config import settings

router = APIRouter()

LANG_FILE = settings.LANG_FILE
USER_FILE = settings.USER_FILE

class UserLang(BaseModel):
    language: str

def _block_browser(accept: str):
    if "text/html" in (accept or "").lower():
        raise HTTPException(status_code=403, detail="errors.forbidden")

# -------------------------------
# Rotas
# -------------------------------
@router.get("/")
async def root(request: Request):
    # 1) Se ainda não tem idioma, vai escolher idioma
    if not LANG_FILE.exists():
        return RedirectResponse("/choose_lang", status_code=303)

    # 2) Se ainda não tem user.json ou não tem senha, vai pro setup
    if not USER_FILE.exists():
        return RedirectResponse("/setup", status_code=303)

    try:
        with USER_FILE.open("r", encoding="utf-8") as f:
            user = json.load(f)
    except Exception:
        # se arquivo corromper, força setup
        return RedirectResponse("/setup", status_code=303)

    if "password" not in user:
        return RedirectResponse("/setup", status_code=303)

    return RedirectResponse("/login", status_code=303)

@router.get("/choose_lang")
async def choose_lang(request: Request):
    has_user = False
    if USER_FILE.exists():
        try:
            with USER_FILE.open("r", encoding="utf-8") as f:
                user = json.load(f)
            has_user = bool(user.get("username"))
        except Exception:
            has_user = False

    return render_template(request, "choose_lang.html", {
        "has_user": has_user,
        "show_footer": False,
    })

@router.post("/api/user/lang", name="set_language")
async def set_language(data: UserLang, accept: str = Header(default="*/*")):
    _block_browser(accept)

    if data.language not in settings.SUPPORTED_LANGS:
        # envia chave i18n para o handler traduzir
        raise HTTPException(400, detail="errors.lang_not_supported")

    lang_data = {"language": data.language}
    with LANG_FILE.open("w", encoding="utf-8") as f:
        json.dump(lang_data, f, indent=2, ensure_ascii=False)
    return {"ok": True}

@router.get("/editor")
async def editor(request: Request):
    # exige login
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    return render_template(request, "editor.html", {
        "data_dir": settings.DATA_DIR,
        "container_name": None,
        "TOTP_ENABLED": settings.TOTP_ENABLED,
        "diff_allow_edit": settings.DIFF_ALLOW_EDIT,
    })