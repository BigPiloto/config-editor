from flask import Flask, redirect, url_for, session, request, abort, g
from flask_login import LoginManager, UserMixin
from pathlib import Path
from config import settings
import json
import xml.etree.ElementTree as ET
import yaml
from markupsafe import Markup
from blueprints.i18n import i18n_bp

# ----------------------------------------------------------------------
# helpers para ler o usuário registrado
# ----------------------------------------------------------------------
def _setup_path() -> Path:
  return Path(settings.STATE_DIR) / "setup.json"
    
def _registered_username() -> str | None:
  p = _setup_path()
  if not p.exists():
    return None
  try:
    st = json.loads(p.read_text())
    if st.get("registered"):
      return (st.get("user") or {}).get("username")
  except Exception:
    pass
  return None

# ----------------------------------------------------------------------
# validação opcional por extensão
# ----------------------------------------------------------------------
def _validate_optional(ext: str, content: str) -> str | None:
  """
  Retorna mensagem de erro (str) se inválido, ou None se estiver ok / sem validador.
  - .xml  → valida bem‑formação
  - .yml/.yaml → valida YAML
  - outros → não bloqueia
  """
  text = content or ""
  ext = (ext or "").lower()

  if ext == ".xml":
    try:
      # Apenas verifica que é bem-formado; DTDs são ignoradas na validação sintática
      ET.fromstring(text.encode("utf-8"))
    except ET.ParseError as e:
      return f"XML inválido: {e}"
    return None

  if ext in (".yml", ".yaml"):
    try:
      yaml.safe_load(text)   # YAML vazio retorna None e é válido
    except Exception as e:
      return f"YAML inválido: {e}"
    return None

  # sem validador para a extensão → não bloqueia o Save
  return None

# ----------------------------------------------------------------------
# I18N simples via JSON
# ----------------------------------------------------------------------
LOCALES_DIR = Path(__file__).parent / "locales"

def _resolve_locale_path(lang: str):
  """
  Retorna o primeiro arquivo de locale existente seguindo a ordem de preferência.
  Preferência: lang -> settings.DEFAULT_LANG -> 'en' -> 'pt-BR'
  """
  candidates = [
    lang,
    getattr(settings, "DEFAULT_LANG", None) or "en",
    "en",
    "pt-BR",
  ]
  for code in candidates:
    path = LOCALES_DIR / f"{code}.json"
    if path.exists():
      return path
  return None

class LocaleStore:
  """Cache simples com auto-reload se arquivo muda (bom em dev)."""
  def __init__(self):
    self._cache = {}
  
  @staticmethod
  def _normalize_lang(code: str) -> str:
    code = (code or "").strip()
    if code.lower().startswith("pt"):
      return "pt-BR"
    if code.lower().startswith("en"):
      return "en"
    return code or "en"
  
  def load(self, lang: str) -> dict:
    lang = self._normalize_lang(lang)
    p = _resolve_locale_path(lang)
    if not p:
      return {}
    mtime = p.stat().st_mtime
    cached = self._cache.get(lang)
    if not cached or cached[0] != mtime:
      # Trata arquivo vazio/JSON inválido: cai para {}
      txt = p.read_text(encoding="utf-8")
      try:
        data = json.loads(txt) if txt.strip() else {}
      except Exception:
        data = {}
      self._cache[lang] = (mtime, data)
    return self._cache[lang][1]
  
  def get(self, lang: str, key: str, default=None, **kwargs):
    """Busca com fallback: lang -> DEFAULT_LANG -> en -> pt-BR.
    Suporta 'dot.path' e formatação .format(**kwargs)."""
    lang = self._normalize_lang(lang)
    def deep_get(dct, dotted):
      cur = dct
      for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
          return None
        cur = cur[part]
      return cur

    # ordem de queda
    fallbacks = [
      lang,
      self._normalize_lang(getattr(settings, "DEFAULT_LANG", "en")),
      "en",
      "pt-BR",
    ]
    for code in fallbacks:
      data = self.load(code)
      val = deep_get(data, key)
      if val is not None:
        if isinstance(val, str):
          if kwargs:
            try:
              val = val.format(**kwargs)
            except Exception:
              pass
          return val
        return val
    # não achou em nenhum fallback: retorna a própria key
    return default if default is not None else key

locale_store = LocaleStore()

def detect_lang():
  """Escolhe o idioma: ?lang= -> session -> header -> DEFAULT_LANG."""
  q = (request.args.get("lang") or "").strip()
  if q and q in settings.SUPPORTED_LANGS:
    session["lang"] = q
    return q
  
  # 1) session
  s = session.get("lang")
  if s in settings.SUPPORTED_LANGS:
    return s

  # 2) cookie
  ck = request.cookies.get("lang", "").strip()
  if ck in settings.SUPPORTED_LANGS:
    session["lang"] = ck
    return ck
  if ck.startswith("pt"):
    if "pt-BR" in settings.SUPPORTED_LANGS:
      session["lang"] = "pt-BR"; return "pt-BR"
    if ck.startswith("en"):
      if "en" in settings.SUPPORTED_LANGS:
        session["lang"] = "en"; return "en"
  
  # 3) Accept-Language (como já estava)
  hdr = request.headers.get("Accept-Language", "")
  if hdr:
    # pega códigos tipo "pt-BR", "en", na ordem
    prefs = [seg.split(";")[0].strip() for seg in hdr.split(",")]
    for pref in prefs:
      if pref in settings.SUPPORTED_LANGS:
        return pref
      # mapear pt -> pt-BR e en-US -> en, etc.
      if pref.startswith("pt") and "pt-BR" in settings.SUPPORTED_LANGS:
        return "pt-BR"
      if pref.startswith("en"):
        if pref.startswith("en") and "en" in settings.SUPPORTED_LANGS:
          return "en"

  return getattr(settings, "DEFAULT_LANG", "en")

def T(key: str, safe: bool=False, default=None, **kwargs):
  """Helper de tradução para usar no Python."""
  lang = getattr(g, "current_lang", getattr(settings, "DEFAULT_LANG", "en"))
  s = locale_store.get(lang, key, default=default, **kwargs)
  return Markup(s) if safe else s

# ----------------------------------------------------------------------
# App Factory
# ----------------------------------------------------------------------
def create_app():
  app = Flask(__name__, template_folder="templates", static_folder="static")
  app.secret_key = settings.FLASK_SECRET_KEY

  # qualidade de vida em dev (auto-reload de templates e sem cache de estáticos)
  app.config.update(
    TEMPLATES_AUTO_RELOAD=True,
    SEND_FILE_MAX_AGE_DEFAULT=0,
    JSON_AS_ASCII=False,
    SUPPORTED_LANGS=getattr(settings, "SUPPORTED_LANGS", ["en", "pt-BR"]),
    DEFAULT_LANG=getattr(settings, "DEFAULT_LANG", "en"),
  )

  # garantir pastas de dados
  Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
  Path(settings.BACKUP_DIR).mkdir(parents=True, exist_ok=True)
  Path(settings.STATE_DIR).mkdir(parents=True, exist_ok=True)

  # [ADD] — expor flags e função para os blueprints
  app.config["DRY_RUN"] = settings.DRY_RUN
  app.config["VALIDATE_OPTIONAL_FN"] = _validate_optional

  @app.after_request
  def _persist_lang(resp):
    lang = session.get("lang")
    if lang:
      # 1 ano; Lax evita envio em cross-site POST
      resp.set_cookie("lang", lang, max_age=60*60*24*365, samesite="Lax")
    return resp

  # idioma inicial na sessão
  @app.before_request
  def _ensure_lang():
    if "lang" not in session:
      initial = app.config["DEFAULT_LANG"] or "en"
      if initial not in app.config["SUPPORTED_LANGS"]:
        initial = "en"
      session["lang"] = initial

  # setar lang resolvido a cada request
  @app.before_request
  def _i18n_before():
    g.current_lang = detect_lang()
  
  # i18n + injeções globais (apenas UM context_processor)
  @app.context_processor
  def _global_ctx():
    def t_filter(key, default=None, **kwargs):
      return Markup.escape(T(key, default=default, **kwargs))
    return {
      "dry_run": settings.DRY_RUN,
      "totp_enabled": settings.TOTP_ENABLED,
      "TOTP_ENABLED": settings.TOTP_ENABLED,
      "T": T,
      "t": t_filter,
      "current_lang": getattr(g, "current_lang", settings.DEFAULT_LANG),
      "supported_langs": app.config["SUPPORTED_LANGS"],
      "data_dir": settings.DATA_DIR,
    }

  def _is_registered() -> bool:
    p = _setup_path()
    if not p.exists():
      return False
    try:
      st = json.loads(p.read_text(encoding="utf-8"))
      return bool(st.get("registered"))
    except Exception:
      return False

  @app.before_request
  def _lang_gate():
    if request.path == "/favicon.ico":
      return
    # liberar estáticos e as próprias rotas do i18n
    ep = request.endpoint or ""
    if ep in ("static", "i18n.choose_lang", "i18n.apply_lang", "i18n.set_lang", "health"):
      return
    
    # se ainda não registrou e não confirmou idioma, manda pro /lang
    if not _is_registered() and not session.get("lang_confirmed"):
      # usa apenas path (+ query) e remove '?' sobrando
      nxt = request.full_path if request.query_string else request.path
      if nxt.endswith("?"):
        nxt = nxt[:-1]
      return redirect(url_for("i18n.choose_lang", next=nxt))


  # Login
  login_manager = LoginManager()
  login_manager.login_view = "auth.login"
  login_manager.session_protection = "strong"
  login_manager.init_app(app)

  class User(UserMixin):
    def __init__(self, username): 
      self.id = username

  @login_manager.user_loader
  def load_user(user_id):
    username = _registered_username()
    return User(user_id) if (username and user_id == username) else None

  # Blueprints
  from blueprints.auth import auth_bp
  from blueprints.editor import editor_bp
  app.register_blueprint(i18n_bp)
  app.register_blueprint(auth_bp)
  app.register_blueprint(editor_bp)

  @app.route("/")
  def index():
      return redirect(url_for("editor.view_editor"))

  @app.route("/health")
  def health():
    return "ok", 200

  app.jinja_env.globals.update(T=T)

  return app

# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=settings.DEBUG)