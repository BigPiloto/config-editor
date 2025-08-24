from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from config import settings
from pathlib import Path
from xml.etree import ElementTree as ET
import subprocess
import json
import yaml
from .utils import (
    ensure_inside, list_data_files, backup_file_for, list_backups_for, safe_write_text
)

editor_bp = Blueprint("editor", __name__, url_prefix="/editor")

def _T(key: str, default=None, **kwargs) -> str:
  """Proxy para T() do Jinja, com fallback seguro."""
  T_fn = current_app.jinja_env.globals.get("T")
  if callable(T_fn):
    return T_fn(key, default=default, **kwargs)
  return default if default is not None else key

def _log_debug(msg, **extra):
  if settings.DEBUG:
    try:
      current_app.logger.debug(msg, extra=extra)
    except Exception:
      # fallback simples
      current_app.logger.debug(f"{msg} | {extra}")

@editor_bp.route("/health")
@login_required
def health():
  results = {}
  containers = sorted(set(settings.FILE_CONTAINERS.values()))
  for name in containers:
    try:
      out = subprocess.check_output(
        ["docker", "inspect", name, "--format", "{{json .State}}"],
        text=True
      )
      state = json.loads(out)
      results[name] = {
        "ok": True,
        "status": state.get("Status"),
        "health": (state.get("Health") or {}).get("Status")
      }
    except Exception as e:
      results[name] = {"ok": False, "error": str(e)}
  return jsonify({"ok": True, "containers": results})

@editor_bp.before_request
def _require_login_for_editor():
  # Qualquer rota do blueprint /editor exige autenticação
  if not current_user.is_authenticated:
    return redirect(url_for("auth.login"))
    
def _read_text(path):
  p = Path(path)
  return p.read_text(encoding="utf-8") if p.exists() else ""

def _validate_xml(text: str):
  try:
    ET.fromstring(text.encode("utf-8"))
    return True, None
  except Exception as e:
    return False, str(e)

def _infer_kind(file_name: str | None) -> str:
  n = (file_name or "").lower()
  
  if n.endswith(".xml"):
    return "xml"
  if n.endswith(".yml") or n.endswith(".yaml"):
    return "yaml"
  return "file"

def _validate_by_kind(text: str, file_name: str | None):
  kind = _infer_kind(file_name)

  if kind == "xml":
    try:
      ET.fromstring((text or "").encode("utf-8"))
      return True, None
    except ET.ParseError as e:
      return False, _T("swal.validate.xml_error", default=f"Invalid XML: {e}", err=str(e))

  if kind in ("yaml", "yml"):
    try:
      yaml.safe_load(text or "")
      return True, None
    except Exception as e:
      return False, _T("swal.validate.yaml_error", default=f"Invalid YAML: {e}", err=str(e))

  return False, _T("swal.validate.no_validator", default="No validator for this file type")

def _current_or_first(file_name: str | None):
  files = list_data_files(settings.DATA_DIR)
  if not files:
    return None, []
  if file_name:
    for f in files:
      if f["name"] == file_name:
        return f, files
  return files[0], files

def _get_optional_validator():
  # Fallback para função no-op que não bloqueia salvamento
  return current_app.config.get("VALIDATE_OPTIONAL_FN", lambda _ext, _text: None)

@editor_bp.route("/")
@login_required
def view_editor():
  file_name = request.args.get("file")
  current, files = _current_or_first(file_name)
  container_name = None
  if current:
    container_name = settings.FILE_CONTAINERS.get(current["name"])
  if not current:
    flash(_T("flash.no_files", default="No files available in /data."), "warning")
    return render_template(
      "editor.html",
      content="",
      backups=[],
      files=[],
      current_file=None,
      dry_run=settings.DRY_RUN,
      container_name=container_name,
      diff_allow_edit=settings.DIFF_ALLOW_EDIT
    )
  path = ensure_inside(settings.DATA_DIR, current["path"])
  content = _read_text(path)
  backups = list_backups_for(settings.BACKUP_DIR, current["name"])
  return render_template(
    "editor.html",
    content=content,
    backups=backups,
    files=files,
    current_file=current,
    dry_run=settings.DRY_RUN,
    container_name=container_name,
    diff_allow_edit=settings.DIFF_ALLOW_EDIT
  )

@login_required
@editor_bp.route("/files")
def files_api():
  q = request.args.get("q")
  return jsonify(list_data_files(settings.DATA_DIR, q))

@editor_bp.route("/validate", methods=["POST"])
@login_required
def validate():
  payload = request.get_json(silent=True)
  if payload:
    file_name = (payload.get("file") or "").strip()
    new_text = payload.get("text","")
  else:
    file_name = request.form.get("file","").strip()
    new_text = request.form.get("text","")

  ok, err = _validate_by_kind(new_text, file_name)
  return jsonify({"ok": ok, "error": err, "kind": _infer_kind(file_name)})

@login_required
@editor_bp.route("/save", methods=["POST"])
def save():
  # aceita JSON ou form-data
  payload = request.get_json(silent=True)
  if payload:
    file_name = (payload.get("file") or "").strip()
    new_text = payload.get("text", "")
  else:
    file_name = request.form.get("file", "").strip()
    new_text = request.form.get("text", "")
  
  if not file_name:
    flash(_T("flash.file_missing", default="File not provided."), "error")
    return redirect(url_for("editor.view_editor"))

  target = ensure_inside(settings.DATA_DIR, str(Path(settings.DATA_DIR) / file_name))

  # usa validador opcional do app
  validator = _get_optional_validator()
  err = validator(Path(file_name).suffix, new_text)
  if err:
    flash(err, "error")
    return redirect(url_for("editor.view_editor", file=file_name))

  # dry-run → não escreve em disco
  if settings.DRY_RUN:
    flash(_T("flash.saved_dry_run", default="Saved (dry-run, nothing written to disk)."), "success")
    return redirect(url_for("editor.view_editor", file=file_name))
  
  # backup + escrita
  backup_path = backup_file_for(target, settings.BACKUP_DIR)
  safe_write_text(target, new_text)

  # mensagem formatada com backup em <small>
  rel_backup = Path(backup_path).relative_to(settings.BACKUP_DIR)
  flash({
    "title": _T("flash.save_ok_title", default="File saved and applied successfully."),
    "html":  _T("flash.save_ok_backup", default="Backup at: {path}", path=str(rel_backup))
  }, "success")

  _log_debug("SAVE", file=file_name, target=str(target), backup=str(rel_backup))
  return redirect(url_for("editor.view_editor", file=file_name))

@login_required
@editor_bp.route("/apply", methods=["POST"])
def apply():
  # aceita JSON ou form-data
  payload = request.get_json(silent=True)
  if payload:
    file_name = (payload.get("file") or "").strip()
    new_text = payload.get("text", "")
  else:
    file_name = request.form.get("file", "").strip()
    new_text = request.form.get("text", "")
  
  if not file_name:
    flash(_T("flash.file_missing", default="File not provided."), "error")
    return redirect(url_for("editor.view_editor"))

  target = ensure_inside(settings.DATA_DIR, str(Path(settings.DATA_DIR) / file_name))

  # usa validador opcional do app
  validator = _get_optional_validator()
  err = validator(Path(file_name).suffix, new_text)
  if err:
    flash(err, "error")
    return redirect(url_for("editor.view_editor", file=file_name))

  # dry-run → não escreve em disco
  if settings.DRY_RUN:
    flash(_T("flash.applied_dry_run", default="Applied (dry-run, no backup; nothing written to disk)."), "success")
    return redirect(url_for("editor.view_editor", file=file_name))
  
  # escrita SEM backup
  safe_write_text(target, new_text)

  # mensagem formatada com backup em <small>
  flash(_T("flash.applied_ok", default="Applied as current version (no backup)."), "success")
  _log_debug("APPLY", file=file_name, target=str(target))
  return redirect(url_for("editor.view_editor", file=file_name))


@login_required
@editor_bp.route("/restart", methods=["POST"])
def restart_container():
  file_name = (request.form.get("file") or "").strip()
  if not file_name:
    flash(_T("flash.restart.file_missing", default="File not provided to restart container."), "error")
    return redirect(url_for("editor.view_editor"))

  container_name = settings.FILE_CONTAINERS.get(file_name)
  if not container_name:
    flash(_T("flash.restart.no_mapping", default="No container associated with this file."), "error")
    return redirect(url_for("editor.view_editor", file=file_name))

  try:
    subprocess.check_call(["docker", "restart", container_name])
    flash(_T("flash.restart.ok", default="Container restarted: {name}", name=container_name), "success")
    _log_debug("RESTART", container=container_name)
  except Exception as e:
    flash(_T("flash.restart.fail", default="Failed to restart: {err}", err=str(e)), "warning")

  return redirect(url_for("editor.view_editor", file=file_name))

@login_required
@editor_bp.route("/restore", methods=["POST"])
def restore():
  file_name = request.form.get("file","").strip()
  backup_path = request.form.get("backup_path","").strip()
  if not file_name or not backup_path:
    flash(_T("flash.restore.missing_params", default="Select file and backup."), "error")
    return redirect(url_for("editor.view_editor", file=file_name or None))

  # Garante que o backup está dentro de BACKUP_DIR antes de ler
  safe_backup = ensure_inside(settings.BACKUP_DIR, backup_path)
  text = _read_text(safe_backup)

  # Valida conteúdo do backup antes de aplicar
  ok, err = _validate_by_kind(text, file_name)
  if not ok:
    flash(_T("flash.restore.bad_backup", default="Corrupted backup: {err}", err=str(err)), "error")
    return redirect(url_for("editor.view_editor", file=file_name))
  
  # Garante que o destino está dentro de DATA_DIR
  target = ensure_inside(settings.DATA_DIR, str(Path(settings.DATA_DIR) / file_name))
  safe_write_text(target, text)

  flash(_T("flash.restore.ok", default="Restored successfully."), "success")
  _log_debug("RESTORE", file=file_name, backup=str(safe_backup), target=str(target))
  return redirect(url_for("editor.view_editor", file=file_name))

@editor_bp.route("/preview", methods=["GET"])
@login_required
def preview():
  file_name = request.args.get("file","").strip()
  backup_path = request.args.get("backup","").strip()
  if not file_name or not backup_path:
    return jsonify({"ok": False, "error": _T("api.invalid_params", default="Invalid parameters")}), 400
  try:
    # segurança: garante que o backup solicitado está dentro de BACKUP_DIR
    safe_path = ensure_inside(settings.BACKUP_DIR, backup_path)
    text = Path(safe_path).read_text(encoding="utf-8")
    return jsonify({"ok": True, "content": text})
  except Exception as e:
    return jsonify({"ok": False, "error": str(e)}), 500

@editor_bp.post("/delete-backup")
@login_required
def delete_backup():
  data = request.get_json(silent=True) or {}
  backup_val = (data.get("backup") or "").strip()
  fname = (data.get("file") or "").strip()

  if not backup_val or backup_val == "__original__" or not fname:
    return jsonify(ok=False, error=_T("api.invalid_params", default="Invalid parameters")), 400

  # Normaliza e garante que está dentro do diretório de backups
  base = Path(settings.BACKUP_DIR).resolve()
  # Se você coloca caminhos relativos no <option value>, resolva contra 'base'
  target = (base / backup_val).resolve() if not backup_val.startswith(str(base)) else Path(backup_val).resolve()

  if not str(target).startswith(str(base)):
    return jsonify(ok=False, error=_T("api.backup_out_of_scope", default="Path outside backup area")), 400
  if not target.exists() or not target.is_file():
    return jsonify(ok=False, error=_T("api.file_not_found", default="File not found")), 404

  try:
    target.unlink()
    return jsonify(ok=True)
  except Exception as e:
    return jsonify(ok=False, error=str(e)), 500