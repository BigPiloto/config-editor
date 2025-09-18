# backend/routes/settings.py
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
import json, io, pyotp, qrcode, os
from passlib.hash import bcrypt

from ..core.templates import render_template
from ..core.context import get_current_lang
from .deps import require_user
from ..core.totp import verify_totp
from ..i18n import t
from ..config import settings

USER_FILE = settings.USER_FILE

DEFAULT_CONTAINER = os.getenv("DEFAULT_CONTAINER", "config-editor")
CONTAINER_ALIAS   = os.getenv("CONTAINER_ALIAS", DEFAULT_CONTAINER)


router = APIRouter()

# ---------------------------------------------------------------------
# Alterar Username
# ---------------------------------------------------------------------
@router.get("/change-username", name="settings.change_username")
async def change_username_form(request: Request, user=Depends(require_user)):
    current_username = None
    totp_required = False

    if USER_FILE.exists():
        with USER_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            current_username = data.get("username")
            totp_required = settings.TOTP_ENABLED and bool(data.get("totp_secret"))

    return render_template(request, "change_username.html", {
        "current_username": current_username,
        "totp_required": totp_required,
        "show_footer": False,
    })

@router.post("/change-username")
async def change_username_submit(
    request: Request,
    username: str = Form(...),
    current: str = Form(...),
    totp: str | None = Form(None),
    user=Depends(require_user),
):
    lang = get_current_lang()

    if not USER_FILE.exists():
        return JSONResponse({"error": t(lang, "errors.userfile_missing")}, status_code=400)

    with USER_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    current_username = data.get("username")
    password_hash = data.get("password")
    totp_secret = data.get("totp_secret")
    totp_required = settings.TOTP_ENABLED and bool(totp_secret)

    # validar senha atual
    if not password_hash or not bcrypt.verify(current, password_hash):
        return JSONResponse({"error": t(lang, "flash.pass_wrong")}, status_code=400)

    # validar TOTP se necessário
    if totp_required and not verify_totp(totp_secret, totp):
        return JSONResponse({"error": t(lang, "flash.2fa_invalid")}, status_code=400)

    # normalizar e validar novo username
    username = (username or "").strip()

    # vazio
    if not username:
        return JSONResponse({"error": t(lang, "errors.username_required")}, status_code=400)
    
    if username == (current_username or ""):
        return JSONResponse({"error": t(lang, "flash.new_user_diff")}, status_code=400)

    # salvar novo usuário
    data["username"] = username
    with USER_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # atualiza sessão
    request.session["username"] = username

    return JSONResponse({"ok": True, "msg": t(lang, "flash.user_changed_success")})

# ---------------------------------------------------------------------
# Alterar Senha
# ---------------------------------------------------------------------
@router.get("/change-password", name="settings.change_password")
async def change_password_form(request: Request, user=Depends(require_user)):
    totp_required = False

    if USER_FILE.exists():
        with USER_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            totp_required = settings.TOTP_ENABLED and bool(data.get("totp_secret"))

    return render_template(request, "change_password.html", {
        "totp_required": totp_required,
        "show_footer": False,
    })


@router.post("/change-password")
async def change_password_submit(
    request: Request,
    current: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    totp: str | None = Form(None),
    user=Depends(require_user),
):
    lang = get_current_lang()

    if not USER_FILE.exists():
        return JSONResponse({"error": t(lang, "errors.userfile_missing")}, status_code=400)

    with USER_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    password_hash = data.get("password")
    totp_secret   = data.get("totp_secret")
    totp_required = settings.TOTP_ENABLED and bool(totp_secret)

    # conferir senha atual
    if not password_hash or not bcrypt.verify(current, password_hash):
        return JSONResponse({"error": t(lang, "flash.pass_wrong")}, status_code=400)

    # conferir TOTP se necessário
    if totp_required and not verify_totp(totp_secret, totp):
        return JSONResponse({"error": t(lang, "flash.2fa_invalid")}, status_code=400)

    # bloquear nova senha igual à atual
    if new_password == current:
        return JSONResponse({"error": t(lang, "errors.password_same_as_current")}, status_code=400)

    # validar nova senha
    if not new_password or new_password != confirm_password:
        return JSONResponse({"error": t(lang, "flash.pass_mismatch")}, status_code=400)

    # salvar hash novo
    new_hash = bcrypt.hash(new_password)
    data["password"] = new_hash
    with USER_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return JSONResponse({"ok": True, "msg": t(lang, "flash.pass_changed_success")})

# ---------------------------------------------------------------------
# Gerenciar TOTP (ativar/desativar)
# ---------------------------------------------------------------------
@router.get("/totp-manage", name="settings.totp_manage")
async def totp_manage_page(request: Request, user=Depends(require_user)):
    if not settings.TOTP_ENABLED:
        return RedirectResponse("/editor", status_code=303)

    with USER_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    secret = data.get("totp_secret")
    status_enabled = bool(secret)

    if not status_enabled and "enable_secret" not in request.session:
        request.session["enable_secret"] = pyotp.random_base32()

    return render_template(request, "totp_manage.html", {
        "status_enabled": status_enabled,
        "username": data.get("username"),
        "show_qr": not status_enabled,
        "show_footer": False,
    })


@router.post("/totp-manage", name="settings.totp_manage_post")
async def totp_manage_post(
    request: Request,
    action: str = Form(...),
    current: str = Form(...),
    totp: str = Form(...),
    user=Depends(require_user),
):
    lang = get_current_lang()

    if not settings.TOTP_ENABLED:
        return JSONResponse({"error": t(lang, "flash.2fa_disable_admin")}, status_code=400)

    with USER_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    secret = data.get("totp_secret")

    # Confere senha
    if not data.get("password") or not bcrypt.verify(current, data["password"]):
        return JSONResponse({"error": t(lang, "flash.pass_wrong")}, status_code=400)

    # Enable
    if action == "enable":
        preview_secret = request.session.get("enable_secret")
        if not preview_secret:
            return JSONResponse({"error": t(lang, "flash.failed_temp_secret")}, status_code=400)

        if not verify_totp(preview_secret, totp):
            return JSONResponse({"error": t(lang, "flash.2fa_invalid_activation")}, status_code=400)

        # Ativa 2FA
        data["totp_secret"] = preview_secret
        with USER_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        request.session.pop("enable_secret", None)
        return JSONResponse({"ok": True, "msg": t(lang, "flash.2fa_enabled_success")})

    # Disable
    if action == "disable":
        if not secret:
            return JSONResponse({"error": t(lang, "flash.2fa_already_disabled")}, status_code=400)

        if not verify_totp(secret, totp):
            return JSONResponse({"error": t(lang, "flash.2fa_invalid")}, status_code=400)

        data.pop("totp_secret", None)
        with USER_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return JSONResponse({"ok": True, "msg": t(lang, "flash.2fa_disabled")})

    return JSONResponse({"error": t(lang, "flash.invalid_action")}, status_code=400)


# ---------------------------------------------------------------------
# QR Codes de TOTP
# ---------------------------------------------------------------------
@router.get("/totp-qr", name="settings.totp_qr")
async def totp_qr(request: Request, user=Depends(require_user)):
    if not settings.TOTP_ENABLED:
        return RedirectResponse("/editor", status_code=303)

    with USER_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    secret = data.get("totp_secret")
    if not secret:
        # rota de imagem → 404 padrão
        raise HTTPException(404, detail=t(get_current_lang(), "errors.no_totp_configured"))

    username = data.get("username", "user")
    uri = pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name="Config Editor")

    qr = qrcode.make(uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.get("/totp-qr-preview", name="settings.totp_qr_preview")
async def totp_qr_preview(request: Request, user=Depends(require_user)):
    if not settings.TOTP_ENABLED:
        return RedirectResponse("/editor", status_code=303)

    preview_secret = request.session.get("enable_secret")
    if not preview_secret:
        raise HTTPException(404, detail=t(get_current_lang(), "errors.preview_secret_missing"))

    with USER_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    username = data.get("username", "user")

    uri = pyotp.TOTP(preview_secret).provisioning_uri(name=username, issuer_name="Config Editor")
    qr = qrcode.make(uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
