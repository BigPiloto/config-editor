# backend/app.py
import logging
from pathlib import Path
import json, os
from hashlib import sha1
from typing import Optional
from fastapi import FastAPI, Request, Header, Response, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from .i18n import load_locale, t
from .routes import router as routes_router
from .core.templates import templates, render_template
from .core.context import get_current_lang
from .config import settings

logger = logging.getLogger(__name__)

BASE_PATH = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_PATH / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

app = FastAPI(title="Config Editor")

# Globais disponíveis em todos templates (produção)
templates.env.globals.update({
    "TOTP_ENABLED": settings.TOTP_ENABLED,
    "DEFAULT_LANG": settings.DEFAULT_LANG,
    "default_container": os.getenv("DEFAULT_CONTAINER", "config-editor"),
    "container_display_name": os.getenv("CONTAINER_ALIAS") or os.getenv("DEFAULT_CONTAINER", "config-editor"),
})

# habilitar sessões (necessário pro login/logout funcionar)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    same_site="lax",
    https_only=settings.HTTPS_ONLY,
)

# incluir rotas registradas
app.include_router(routes_router)

# -------------------------------
# Helpers — sem vazar detalhes
# -------------------------------
def wants_json(request: Request) -> bool:
    if request.url.path.startswith("/api/"):
        return True
    accept = (request.headers.get("accept") or "").lower()
    return "application/json" in accept

def json_error(lang: str, code: str, message_key: str, status: int, detail=None):
    payload = {
        "ok": False,
        "error": {
            "code": code,
            "message": t(lang, message_key),
        },
    }
    return JSONResponse(payload, status_code=status)

# -------------------------------
# Rotas utilitárias
# -------------------------------

# rota i18n (frontend consome via fetch) — com Cache-Control + ETag + 304
@app.get("/i18n/{lang}")
def get_locale(lang: str, if_none_match: Optional[str] = Header(default=None)):
    data = load_locale(lang)
    # hash estável do conteúdo (chaves ordenadas)
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    etag = '"' + sha1(raw).hexdigest() + '"'

    # Revalidação condicional
    if if_none_match and etag in [tag.strip() for tag in if_none_match.split(",")]:
        return Response(status_code=304, headers={
            "ETag": etag,
            "Cache-Control": "public, max-age=3600",
        })

    return JSONResponse(
        data,
        headers={
            "ETag": etag,
             "Cache-Control": "public, max-age=3600",
        }
    )

# servir estáticos
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    lang = settings.DEFAULT_LANG
    logger.warning("%s: %s", t(lang, "errors.static_not_found"), STATIC_DIR)

# -------------------------------
# Handlers de erro (sem detalhes)
# -------------------------------
def render_error(request: Request, template: str, status_code: int, detail: str = None):
    return render_template(
        request,
        template,
        {"show_footer": False, "detail": detail},
        status_code=status_code,
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    lang = get_current_lang(request)

    # APIs → JSON padronizado (sem detail)
    if wants_json(request):
        mapping = {
            401: ("not_authenticated", "errors.not_authenticated"),
            403: ("forbidden", "errors.forbidden"),
            404: ("not_found", "errors.not_found"),
            405: ("method_not_allowed", "errors.method_not_allowed"),
            409: ("conflict", "errors.http_error"),
        }
        code, default_key = mapping.get(exc.status_code, ("http_error", "errors.http_error"))

        # Para 4xx, usamos a mensagem específica que a rota enviou em `detail`
        if exc.status_code < 500 and isinstance(exc.detail, str):
            if exc.detail.startswith("errors."):
                msg = t(lang, exc.detail)
            else:
                msg = exc.detail
        else:
            msg = t(lang, default_key)

        return JSONResponse(
            {"ok": False, "error": {"code": code, "message": msg}},
            status_code=exc.status_code,
        )
        
    # HTML → páginas i18n conhecidas
    if exc.status_code == 401:
        return render_error(request, "401.html", 401, t(lang, "errors.not_authenticated"))
    if exc.status_code == 403:
        return render_error(request, "403.html", 403, t(lang, "errors.forbidden"))
    if exc.status_code == 404:
        return render_error(request, "404.html", 404, t(lang, "errors.not_found"))
    if exc.status_code == 405:
        return render_error(request, "405.html", 405, t(lang, "errors.method_not_allowed"))

    # Fallback: mensagem genérica i18n
    return render_error(request, "500.html", exc.status_code, t(lang, "errors.http_error"))

@app.exception_handler(Exception)
async def server_error_handler(request: Request, exc: Exception):
    lang = get_current_lang(request)
    # Loga stack trace completo no servidor
    logger.exception("Unhandled server error")

    if wants_json(request):
        return json_error(lang, "internal_error", "errors.internal_error", 500, detail=exc)

    # HTML 500 sem detalhes técnicos
    return render_error(request, "500.html", 500, t(lang, "errors.internal_error"))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    lang = get_current_lang(request)

    if wants_json(request):
        return JSONResponse(
            {
                "ok": False,
                "error": {
                    "code": "validation_error",
                    "message": t(lang, "errors.validation_error"),
                    "fields": exc.errors(),
                }
            },
            status_code=422,
        )
        
    # Páginas HTML → mensagem curta i18n
    return PlainTextResponse(t(lang, "errors.validation_error"), status_code=422)

@app.middleware("http")
async def enforce_https(request, call_next):
    if settings.HTTPS_ONLY:
        proto = request.headers.get("x-forwarded-proto") or request.url.scheme
        if proto != "https":
            # redireciono temporário p/ evitar cache permanente
            if request.method in ("GET", "HEAD"):
                return RedirectResponse(str(request.url.replace(scheme="https")), status_code=307)
            raise HTTPException(403, detail="errors.forbidden")

    resp = await call_next(request)

    if settings.HTTPS_ONLY:
        host = (request.headers.get("host") or "").split(":")[0]
        # não manda HSTS para hosts de desenvolvimento
        if host not in ("localhost", "127.0.0.1", "[::1]"):
            resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return resp