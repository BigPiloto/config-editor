from flask import Blueprint, render_template, request, redirect, url_for, session, abort, current_app
from urllib.parse import urlparse

i18n_bp = Blueprint("i18n", __name__, url_prefix="")

@i18n_bp.get("/lang")
def choose_lang():
  next_url = request.args.get("next") or url_for("auth.setup")
  return render_template(
    "choose_lang.html",
    supported=current_app.config["SUPPORTED_LANGS"],
    current=session.get("lang") or current_app.config["DEFAULT_LANG"],
    next_url=next_url,
  )

@i18n_bp.post("/lang")
def apply_lang():
  lang = (request.form.get("lang") or "").strip()
  if lang in current_app.config["SUPPORTED_LANGS"]:
    session["lang"] = lang
  session["lang_confirmed"] = True
  next_url = request.form.get("next_url")
  if not _is_safe_next(next_url):
    next_url = url_for("auth.setup")
  return redirect(next_url)

@i18n_bp.get("/set-lang/<lang>")
def set_lang(lang):
  if lang not in current_app.config["SUPPORTED_LANGS"]:
    abort(404)
  session["lang"] = lang
  next_url = request.args.get("next")
  if not _is_safe_next(next_url):
    next_url = url_for("i18n.choose_lang")
  return redirect(next_url)

def _is_safe_next(next_url: str | None) -> bool:
  if not next_url:
    return False
  u = urlparse(next_url)
  # só permite caminhos relativos no mesmo host (sem esquema/domínio)
  return (not u.scheme) and (not u.netloc) and next_url.startswith("/")