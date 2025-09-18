# backend/routes/auth.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, StreamingResponse
import json, pyotp, io, qrcode
from passlib.hash import bcrypt

from ..core.templates import render_template
from ..core.totp import verify_totp, generate_totp_uri
from ..config import settings

router = APIRouter()

# usa paths centralizados do config
USER_FILE = settings.USER_FILE

# -------------------------------
# 🔐 LOGIN / LOGOUT
# -------------------------------
@router.get("/login", name="login")
async def login(request: Request):
    # sessão ativa → editor
    if request.session.get("username"):
        return RedirectResponse("/editor", status_code=303)

    # sem user.json ou inválido → setup
    if not USER_FILE.exists():
        return RedirectResponse("/setup", status_code=303)
    try:
        with USER_FILE.open("r", encoding="utf-8") as f:
            user = json.load(f)
        if "username" not in user or "password" not in user:
            return RedirectResponse("/setup", status_code=303)
    except Exception:
        return RedirectResponse("/setup", status_code=303)

    totp_required = settings.TOTP_ENABLED and bool(user.get("totp_secret"))
    return render_template(request, "login.html", {
        "totp_required": totp_required,
        "show_footer": False,
    })

@router.post("/login", name="login_post")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    totp: str | None = Form(None),
):
    # sem user.json → setup
    if not USER_FILE.exists():
        return RedirectResponse("/setup", status_code=303)

    try:
        with USER_FILE.open("r", encoding="utf-8") as f:
            user = json.load(f)
    except Exception:
        return RedirectResponse("/setup", status_code=303)

    posted_user = (username or "").strip()
    stored_user = (user.get("username") or "").strip()
    password_hash = user.get("password")

    valid_user = False
    if password_hash and posted_user == stored_user:
        try:
            valid_user = bcrypt.verify(password, password_hash)
        except Exception:
            valid_user = False

    if not valid_user:
        return render_template(request, "login.html", {
            "error_key": "login.invalid_credentials",
            "totp_required": settings.TOTP_ENABLED and bool(user.get("totp_secret")),
            "show_footer": False,
        })

    # valida TOTP (se habilitado e houver secret salvo)
    if settings.TOTP_ENABLED and user.get("totp_secret"):
        if not verify_totp(user["totp_secret"], totp):
            return render_template(request, "login.html", {
                "error_key": "login.invalid_2fa",
                "totp_required": True,
                "show_footer": False,
            })

    # sucesso → salva sessão
    # limpa dados antigos e cria uma sessão “fresca”
    request.session.clear()
    request.session["username"] = stored_user or posted_user
    return RedirectResponse("/editor", status_code=303)

@router.get("/logout", name="logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

# -------------------------------
# ⚙️ SETUP (primeiro usuário)
# -------------------------------
@router.get("/setup", name="setup")
async def setup(request: Request):
    # já há usuário? → login
    if USER_FILE.exists():
        try:
            with USER_FILE.open("r", encoding="utf-8") as f:
                user = json.load(f)
            if "username" in user and "password" in user:
                return RedirectResponse("/login", status_code=303)
        except Exception:
            pass

    # gera segredo temporário para QR e guarda em sessão
    if settings.TOTP_ENABLED and "reg_secret" not in request.session:
        request.session["reg_secret"] = pyotp.random_base32()

    return render_template(request, "setup.html", {
        "totp_enabled": settings.TOTP_ENABLED,
        "show_qr": settings.TOTP_ENABLED,
        "show_footer": False,
    })

@router.post("/setup", name="setup_post")
async def setup_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    totp: str | None = Form(None),
):
    # já há usuário? → login
    if USER_FILE.exists():
        try:
            with USER_FILE.open("r", encoding="utf-8") as f:
                user = json.load(f)
            if "username" in user and "password" in user:
                return RedirectResponse("/login", status_code=303)
        except Exception:
            pass

    if password != confirm_password:
        return render_template(request, "setup.html", {
            "error_key": "setup.password_mismatch",
            "totp_enabled": settings.TOTP_ENABLED,
            "show_qr": settings.TOTP_ENABLED,
            "show_footer": False,
        })

    hashed = bcrypt.hash(password)
    user_data = {
        "username": (username or "").strip(),
        "password": hashed,
    }

    if settings.TOTP_ENABLED:
        # secret temporário da sessão
        secret = request.session.get("reg_secret")
        if not secret:
            return RedirectResponse("/setup", status_code=303)

        if not totp or not verify_totp(secret, totp):
            return render_template(request, "setup.html", {
                "error_key": "register.2fa.invalid",
                "totp_enabled": settings.TOTP_ENABLED,
                "show_qr": True,
                "show_footer": False,
            })
        user_data["totp_secret"] = secret

    with USER_FILE.open("w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2, ensure_ascii=False)

    # limpa segredo temporário da sessão
    request.session.pop("reg_secret", None)
    request.session.pop("reg_username", None)

    # mostra sucesso no próprio setup (mantém UX)
    return render_template(request, "setup.html", {
        "success_key": "register.success",
        "totp_enabled": settings.TOTP_ENABLED,
        "show_qr": False,
        "show_footer": False,
    })

# -------------------------------
# 📲 QR CODE inicial (setup)
# -------------------------------
@router.get("/setup/qr", name="auth.setup_qr")
async def setup_qr(request: Request, u: str | None = None):
    """Gera um QR code TOTP apenas durante o setup inicial."""
    # 1) TOTP desabilitado → login
    if not settings.TOTP_ENABLED:
        return RedirectResponse("/login", status_code=303)

    # 2) Já existe usuário → login
    if USER_FILE.exists():
        try:
            with USER_FILE.open("r", encoding="utf-8") as f:
                user = json.load(f)
            if "username" in user and "password" in user:
                return RedirectResponse("/login", status_code=303)
        except Exception:
            pass

    # 3) Não há segredo temporário na sessão → setup
    secret = request.session.get("reg_secret")
    if not secret:
        return RedirectResponse("/setup", status_code=303)

    # 4) Monta URI compatível com Google Authenticator / Authy
    username = (u or request.session.get("reg_username") or "user").strip() or "user"
    uri = generate_totp_uri(secret, username)

    # 5) Cria QR code
    qr = qrcode.make(uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )