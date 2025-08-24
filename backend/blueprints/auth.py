from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, session, current_app, make_response
from flask_login import login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import settings
from pathlib import Path
from datetime import datetime
import json, io, pyotp, segno
from urllib.parse import urlparse, urljoin
import os, tempfile, time
from markupsafe import Markup

def _chosen_lang() -> str:
  """Pega o idioma vindo do form, da sessão ou do cookie."""
  supported = set(current_app.config.get("SUPPORTED_LANGS", ["en", "pt-BR"]))
  lang = (request.form.get("lang") or "").strip() \
    or (session.get("lang") or "").strip() \
    or (request.cookies.get("lang") or "").strip()
  
  if lang.lower().startswith("pt"):
    lang = "pt-BR"
  elif lang.lower().startswith("en"):
    lang = "en"

  if lang not in supported:
    lang = current_app.config.get("DEFAULT_LANG", "en")
    if lang not in supported:
      lang = next(iter(supported))
  return lang

def set_lang_and_redirect(lang: str, to: str):
  """Grava sessão + cookie de idioma e redireciona."""
  session["lang"] = lang
  resp = make_response(redirect(to))
  resp.set_cookie("lang", lang, max_age=60*60*24*365, samesite="Lax")
  return resp

def _T(key: str, **kwargs) -> str:
  """
  Busca a função T registrada no Jinja. Se não existir, retorna a própria chave.
  Evita precisar importar T diretamente aqui.
  """
  T_fn = current_app.jinja_env.globals.get("T")
  if callable(T_fn):
    return T_fn(key, **kwargs)
  return key

def flash_t(key: str, category: str = "info", **kwargs):
  """Faz flash de uma mensagem traduzida."""
  msg = _T(key, **kwargs)
  flash(Markup.escape(msg), category)

def response_t(key: str, status: int = 200, **kwargs) -> Response:
  """Cria um Response com corpo traduzido."""
  return Response(_T(key, **kwargs), status)  
  

# ---------------------------------------------------------------------
# Blueprint
# ---------------------------------------------------------------------
auth_bp = Blueprint("auth", __name__, url_prefix="")

class User(UserMixin):
  def __init__(self, username: str) -> None:
    self.id = username

# ---------------------------------------------------------------------
# Persistência do estado (usuário único + segredo TOTP)
# Arquivo: <STATE_DIR>/setup.json
# Estrutura:
# {
#   "registered": true,
#   "user": {"username": "...", "password_hash": "..."},
#   "totp_secret": "...",
#   "created_at": "..."
# }
# ---------------------------------------------------------------------
def _state_path() -> Path:
  p = Path(settings.STATE_DIR) / "setup.json"
  p.parent.mkdir(parents=True, exist_ok=True)
  return p

def _load_state() -> dict:
  p = _state_path()
  if p.exists():
    return json.loads(p.read_text())
  return {}

def _save_state(data: dict) -> None:
  """
  Escreve o JSON de forma atômica quando possível.
  No Windows, se o os.replace() falhar por bloqueio (WinError 32),
  fazemos algumas tentativas com backoff e, por fim, um fallback.
  """
  p = _state_path()
  d = p.parent
  fd, tmp_path = tempfile.mkstemp(dir=d, prefix="setup.", suffix=".tmp")
  try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=2)
      f.flush()
      try:
        os.fsync(f.fileno())
      except OSError:
        pass

    attempts = 10 if os.name == "nt" else 1
    last_exc = None
    for i in range(attempts):
      try:
        os.replace(tmp_path, p)
        last_exc = None
        break
      except PermissionError as e:
        last_exc = e
        time.sleep(0.05 * (i + 1))
    
    if last_exc:
      with open(p, "w", encoding="utf-8", newline="\n") as f2:
        json.dump(data, f2, ensure_ascii=False, indent=2)
        f2.flush()
        try:
          os.fsync(f2.fileno())
        except OSError:
          pass
  finally:
    try:
      if os.path.exists(tmp_path):
        os.remove(tmp_path)
    except OSError:
      pass

def _is_registered() -> bool:
  st = _load_state()
  u = (st.get("user") or {}).get("username")
  ph = (st.get("user") or {}).get("password_hash")
  return bool(st.get("registered") and u and ph)

def _get_user():
  st = _load_state()
  u = (st.get("user") or {}).get("username")
  ph = (st.get("user") or {}).get("password_hash")
  return u, ph

def _get_totp_secret() -> str | None:
  st = _load_state()
  return st.get("totp_secret") or None

def _register_user(username: str, password_hash: str, secret: str | None) -> None:
  data = {
    "registered": True,
    "user": {"username": username, "password_hash": password_hash},
    "created_at": datetime.utcnow().isoformat() + "Z",
  }
  if secret:
    data["totp_secret"] = secret
  _save_state(data)

def _verify_totp_with(secret: str, code: str) -> bool:
  if not secret:
    return False
  return pyotp.TOTP(secret).verify((code or "").strip(), valid_window=1)

def _set_username(username: str):
  st = _load_state()
  st.setdefault("user", {})
  st["user"]["username"] = username
  _save_state(st)

def _set_password_hash(p_hash: str):
  st = _load_state()
  st.setdefault("user", {})
  st["user"]["password_hash"] = p_hash
  _save_state(st)

def _set_totp_secret(secret: str | None):
  st = _load_state()
  if secret:
    st["totp_secret"] = secret
  else:
    st.pop("totp_secret", None)
  _save_state(st)  

def _is_safe_next_url(target: str) -> bool:
  if not target:
    return False
  host_url = urlparse(request.host_url)
  redirect_url = urlparse(urljoin(request.host_url, target))
  return (redirect_url.scheme in ('http', 'https') and
    host_url.netloc == redirect_url.netloc)

# ---------------------------------------------------------------------
# Guard: enquanto não registrar, qualquer rota (exceto setup/QR/static)
# redireciona para /setup
# ---------------------------------------------------------------------
@auth_bp.before_request
def _force_setup_first():
  if _is_registered():
    return
  allowed = {"auth.setup", "auth.setup_qr", "static"}
  endpoint = (request.endpoint or "").split(":")[-1]
  if endpoint not in allowed:
    return redirect(url_for("auth.setup"))

# ---------------------------------------------------------------------
# Registro inicial (primeira execução)
# ---------------------------------------------------------------------
@auth_bp.route("/setup", methods=["GET", "POST"])
def setup():
  # Se já está registrado, nunca mais volta para cá
  if _is_registered():
    return redirect(url_for("auth.login"))

  totp_on = bool(settings.TOTP_ENABLED)

  # Secret temporário mantido em sessão até concluir o registro (apenas se TOTP estiver ligado)
  if totp_on and ("reg_secret" not in session):
    session["reg_secret"] = pyotp.random_base32()
  reg_secret = session.get("reg_secret")

  if request.method == "POST":
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip() 
    confirm  = (request.form.get("confirm")  or "").strip()
    code     = (request.form.get("totp")     or "").strip()

    session["reg_username"] = username

    if not username or not password:
      flash_t("flash.user_pass", "error")
      return render_template("setup.html", totp_enabled=totp_on, show_qr=totp_on)

    if password != confirm:
      flash_t("flash.dont_match", "error")
      return render_template("setup.html", totp_enabled=totp_on, show_qr=totp_on)

    if totp_on:
    # 2FA obrigatório quando o recurso global está habilitado
      if not _verify_totp_with(reg_secret, code):
        flash_t("flash.2fa_invalid", "error")
        return render_template("setup.html", totp_enabled=totp_on, show_qr=totp_on)
      secret_to_save = reg_secret
    else:
      # Sem 2FA: não gera/valida segredo
      secret_to_save = None

    # Persiste usuário único + segredo TOTP
    _register_user(username, generate_password_hash(password), secret_to_save)

    # Limpa secret temporário e realiza login
    if totp_on:
      session.pop("reg_secret", None)
    session.pop("reg_username", None)

    login_user(User(username))

    if totp_on:
      flash_t("flash.user_2fa", "success")
    else:
      flash_t("flash.user_register", "success")
    
    lang = _chosen_lang()
    return set_lang_and_redirect(lang, url_for("editor.view_editor"))

  # GET → mostra card com QR + formulário
  return render_template("setup.html", totp_enabled=totp_on, show_qr=totp_on)

@auth_bp.route("/setup/qr")
def setup_qr():
  """
  Gera o QR a partir do segredo temporário da sessão.
  """
  if not settings.TOTP_ENABLED:
    return response_t("setup.totp_disabled", 404)

  secret = session.get("reg_secret")
  if not secret:
    return response_t("setup.secret_missing", 404)

  username = (request.args.get("u") or session.get("reg_username") or "user").strip() or "user"
  uri = pyotp.TOTP(secret).provisioning_uri(
    name=username,
    issuer_name="Config Editor"
  )
  qr = segno.make(uri, error="m")
  buf = io.BytesIO()
  qr.save(buf, kind="png", scale=5, border=1)
  return Response(
    buf.getvalue(),
    mimetype="image/png",
    headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
  )

# ---------------------------------------------------------------------
# Login normal (após registro)
# ---------------------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
  # Já autenticado → editor
  if current_user.is_authenticated:
    return redirect(url_for("editor.view_editor"))

  error = None
  
  # Se ainda não registrou, o guard acima já redireciona para /setup
  if request.method == "POST":
    u_form = (request.form.get("username") or "").strip()
    p_form = (request.form.get("password") or "").strip()
    code   = (request.form.get("totp")     or "").strip()

    u_saved, p_hash = _get_user()
    if u_saved and (u_form == u_saved) and p_hash and check_password_hash(p_hash, p_form):
      secret = _get_totp_secret()
      totp_required = bool(settings.TOTP_ENABLED and secret)

      if totp_required:
        if not code:
          error = _T("login.2fa_required")
          return render_template("login.html", totp_required=True, error=error)

        if not _verify_totp_with(secret, code):
          error = _T("login.2fa_invalid")
          return render_template(
            "login.html",
            totp_required=True,
            error=error
          )

      session.clear()
      login_user(User(u_saved))

      lang = _chosen_lang()
      nxt = request.args.get("next")
      dest = nxt if _is_safe_next_url(nxt) else url_for("editor.view_editor")
      return set_lang_and_redirect(lang, dest)

    error = _T("login.invalid_credentials")

  # GET ou POST com erro → mostra tela de login
  # Exibe campo 2FA somente se global ON e já houver segredo salvo
  secret = _get_totp_secret()
  totp_required = bool(settings.TOTP_ENABLED and secret)

  return render_template(
    "login.html",
    totp_required=totp_required,
    error=error
  )

# ---------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------
@auth_bp.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for("auth.login"))

# ---------------------------------------------------------------------
# Alterar senha
# ---------------------------------------------------------------------
@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
  secret = _get_totp_secret()
  totp_required = bool(settings.TOTP_ENABLED and secret)

  if request.method == "POST":
    current = (request.form.get("current") or "").strip()
    new     = (request.form.get("new")     or "").strip()
    confirm = (request.form.get("confirm") or "").strip()
    code    = (request.form.get("totp")    or "").strip()

    u_saved, p_hash = _get_user()

    # 1) Confere a senha atual
    if not p_hash or not check_password_hash(p_hash, current):
      flash_t("flash.pass_incorrect", "error")
      return render_template("change_password.html", totp_required=totp_required)

    # 2) Se TOTP requerido, valida o código
    if totp_required:
      if not _verify_totp_with(secret, code):
        flash_t("flash.2fa_invalid", "error")
        return render_template("change_password.html", totp_required=totp_required)

    # 3) Regras básicas para a nova senha
    if not new:
      flash_t("flash.pass_empty", "error")
      return render_template("change_password.html", totp_required=totp_required)

    if new != confirm:
      flash_t("flash.confirm_dont_match", "error")
      return render_template("change_password.html", totp_required=totp_required)

    if current == new:
      flash_t("flash.new_pass_diff", "error")
      return render_template("change_password.html", totp_required=totp_required)

    # 4) Persiste a nova senha
    st = _load_state()
    st.setdefault("user", {})
    st["user"]["password_hash"] = generate_password_hash(new)
    _save_state(st)

    flash_t("flash.sucess_change_pass", "success")
    return redirect(url_for("editor.view_editor"))

  # GET → formulário
  return render_template("change_password.html", totp_required=totp_required)

# ---------------------------------------------------------------------
# Alterar usuário
# ---------------------------------------------------------------------
@auth_bp.route("/change-username", methods=["GET", "POST"])
@login_required
def change_username():
  secret = _get_totp_secret()
  totp_required = bool(settings.TOTP_ENABLED and secret)

  if request.method == "POST":
    new_user = (request.form.get("username") or "").strip()
    current_pass = (request.form.get("current") or "").strip()
    code = (request.form.get("totp") or "").strip()

    u_saved, p_hash = _get_user()

    # Senha obrigatória para autorizar
    if not p_hash or not check_password_hash(p_hash, current_pass):
      flash_t("flash.pass_wrong", "error")
      return render_template("change_username.html", totp_required=totp_required, current_username=u_saved)

    # Se 2FA ativo/global, exige código
    if totp_required and not _verify_totp_with(secret, code):
      flash_t("flash.2fa_invalid", "error")
      return render_template("change_username.html", totp_required=totp_required, current_username=u_saved)

    if not new_user or new_user == u_saved:
      flash_t("flash.new_user_diff", "error")
      return render_template("change_username.html", totp_required=totp_required, current_username=u_saved)

    _set_username(new_user)

    # Atualiza sessão do flask-login
    logout_user()
    login_user(User(new_user))

    flash_t("flash.change_user_sucess", "success")
    return redirect(url_for("editor.view_editor"))

  # GET
  u_saved, _ = _get_user()
  return render_template("change_username.html", totp_required=totp_required, current_username=u_saved)

# ---------------------------------------------------------------------
# Gerenciar TOTP
# ---------------------------------------------------------------------
@auth_bp.route("/totp-manage", methods=["GET", "POST"])
@login_required
def totp_manage():
  if not settings.TOTP_ENABLED:
    flash_t("flash.2fa_disable_admin", "error")
    return redirect(url_for("editor.view_editor"))

  secret = _get_totp_secret()
  u_saved, _ = _get_user()
  status_enabled = bool(secret)

  if not status_enabled and "enable_secret" not in session:
    session["enable_secret"] = pyotp.random_base32()

  if request.method == "POST":
    action = (request.form.get("action") or "").strip()
    current_pass = (request.form.get("current") or "").strip()
    code = (request.form.get("totp") or "").strip()

    _, p_hash = _get_user()
    if not p_hash or not check_password_hash(p_hash, current_pass):
      flash_t("flash.pass_wrong", "error")
      return render_template("totp_manage.html", status_enabled=status_enabled, username=u_saved, show_qr=not status_enabled)

    if action == "enable":
      if status_enabled:
        flash_t("flash.2fa_already_enabled", "error")
        return render_template("totp_manage.html", status_enabled=True, username=u_saved)

      preview_secret = session.get("enable_secret")
      if not preview_secret:
        flash_t("flash.failed_temp_secret", "error")
        return redirect(url_for(".totp_manage"))

      # exige confirmação já com o novo segredo
      if not _verify_totp_with(preview_secret, code):
        flash_t("flash.2fa_invalid_activation", "error")
        return render_template("totp_manage.html", status_enabled=False, username=u_saved, show_qr=True)

      _set_totp_secret(preview_secret)
      session.pop("enable_secret", None)
      flash_t("flash.2fa_enabled_sucess", "success")
      return redirect(url_for(".totp_manage"))

    elif action == "disable":
      if not status_enabled:
        flash_t("flash.2fa_already_disabled", "error")
        return render_template("totp_manage.html", status_enabled=False, username=u_saved)

      if not _verify_totp_with(secret, code):
        flash_t("flash.2fa_invalid", "error")
        return render_template("totp_manage.html", status_enabled=True, username=u_saved)

      _set_totp_secret(None)
      flash_t("flash.2fa_disabled", "success")
      return redirect(url_for(".totp_manage"))

    else:
      flash_t("flash.invalid_action", "error")

  return render_template("totp_manage.html", status_enabled=status_enabled, username=u_saved, show_qr=not status_enabled)


@auth_bp.route("/totp-qr")
@login_required
def totp_qr():
  if not settings.TOTP_ENABLED:
    return response_t("totp.disabled", 404)

  # QR do segredo persistido (estado atual)
  secret = _get_totp_secret()
  if not secret:
    return response_t("totp.no_secret", 404)

  u_saved, _ = _get_user()
  username = u_saved or "user"
  uri = pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name="Config Editor")

  qr = segno.make(uri, error="m")
  buf = io.BytesIO()
  qr.save(buf, kind="png", scale=5, border=1)
  return Response(buf.getvalue(), mimetype="image/png", headers={"Cache-Control": "no-store"})

@auth_bp.route("/totp-qr-preview")
@login_required
def totp_qr_preview():
  if not settings.TOTP_ENABLED:
    return response_t("totp.disabled", 404)

  preview_secret = session.get("enable_secret")
  if not preview_secret:
    return response_t("totp.preview_missing", 404)

  u_saved, _ = _get_user()
  username = u_saved or "user"
  uri = pyotp.TOTP(preview_secret).provisioning_uri(name=username, issuer_name="Config Editor")

  qr = segno.make(uri, error="m")
  buf = io.BytesIO()
  qr.save(buf, kind="png", scale=5, border=1)
  return Response(buf.getvalue(), mimetype="image/png", headers={"Cache-Control": "no-store"})

# ---------------------------------------------------------------------
# Expor rota TOTP
# ---------------------------------------------------------------------
@auth_bp.app_context_processor
def inject_flags():
    return {"TOTP_ENABLED": bool(settings.TOTP_ENABLED)}