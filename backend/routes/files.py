# backend/routes/files.py
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import shutil, json, logging

from ..i18n import t
from ..core.context import get_current_lang
from .deps import require_user, browser_blocker
from ..config import settings
from . import temp

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["files"])

# Raiz do workspace (configurável; fallback para "meus_arquivos")
BASE_DIR = Path(getattr(settings, "DATA_DIR", "meus_arquivos")).resolve()

# Arquivos/diretórios internos que não devem aparecer na árvore/busca
EXCLUDE_NAMES = {".backups", ".tmp", ".file_containers.json"}

INDEX_FILE = BASE_DIR / ".backups" / "index.json"
CONTAINERS_FILE = BASE_DIR / ".file_containers.json"

# ------------------------------- Utilitários -------------------------------

def load_index() -> Dict[str, Any]:
    if INDEX_FILE.exists():
        return json.loads(INDEX_FILE.read_text(encoding="utf-8") or "{}")
    return {}

def save_index(idx: Dict[str, Any]) -> None:
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8")

def load_containers() -> Dict[str, str]:
    if CONTAINERS_FILE.exists():
        try:
            return json.loads(CONTAINERS_FILE.read_text(encoding="utf-8") or "{}")
        except Exception as e:
            logger.warning("Failed to read .file_containers.json: %s", e)
    return {}

def save_containers(mapping: Dict[str, str]) -> None:
    CONTAINERS_FILE.write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")

def safe_path(rel: str) -> Path:
    rel = (rel or "").lstrip("/")
    target = (BASE_DIR / rel).resolve()
    if BASE_DIR not in target.parents and target != BASE_DIR:
        # chave i18n; handler global retorna JSON genérico (sem detail) — OK
        raise HTTPException(400, detail="errors.path_outside_workspace")
    return target

def is_excluded_child(p: Path) -> bool:
    """Retorna True se 'p' (relativo ao BASE_DIR) contiver algum nome reservado."""
    try:
        parts = (p.relative_to(BASE_DIR)).parts
    except Exception:
        return False
    return any(part in EXCLUDE_NAMES for part in parts)

def update_containers_on_move(src_rel: str, dst_rel: str, is_dir: bool) -> None:
    mapping = load_containers()
    changed = False

    if not mapping:
        return

    if not is_dir:
        if src_rel in mapping:
            mapping[dst_rel] = mapping.pop(src_rel)
            changed = True
    else:
        # para diretórios, remapeia todas as entradas com esse prefixo
        prefix = src_rel.rstrip("/") + "/"
        updates = {}
        for k, v in list(mapping.items()):
            if k == src_rel or k.startswith(prefix):
                new_k = k.replace(src_rel, dst_rel, 1)
                updates[new_k] = v
                del mapping[k]
                changed = True
        if updates:
            mapping.update(updates)

    if changed:
        save_containers(mapping)

# ------------------------------- Modelos -------------------------------

class SaveBody(BaseModel):
    path: str
    content: str

class MkdirBody(BaseModel):
    path: str

class MoveBody(BaseModel):
    src: str
    dst: str

class CreateFileBody(BaseModel):
    path: str
    content: Optional[str] = ""

# =========================================================
# Árvores e arquivos
# =========================================================

@router.get("/tree")
def list_dir(
    request: Request,
    path: str = Query("", description="caminho relativo ao workspace"),
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()
    p = safe_path(path)
    if not p.exists():
        raise HTTPException(404, detail=t(lang, "errors.path_not_found"))
    if not p.is_dir():
        raise HTTPException(400, detail=t(lang, "errors.not_dir"))

    dirty_map = temp.load_dirty()

    items = []
    for e in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        # oculta internos
        if e.name in EXCLUDE_NAMES:
            continue
        items.append({
            "name": e.name,
            "is_dir": e.is_dir(),
            "type": "folder" if e.is_dir() else "file",
            "path": str(e.relative_to(BASE_DIR)),
            "dirty": dirty_map.get(str(e.relative_to(BASE_DIR)), False),
        })
    return {"base": str(BASE_DIR), "path": path, "items": items}

@router.get("/file")
def read_file(
    request: Request,
    path: str = Query(...),
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()
    f = safe_path(path)
    if not f.exists() or not f.is_file():
        raise HTTPException(404, detail=t(lang, "errors.file_not_found"))
    try:
        text = f.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise HTTPException(415, detail=t(lang, "errors.not_utf8"))

    st = f.stat()
    return {
        "path": path,
        "content": text,
        "mtime": int(st.st_mtime),
        "size": st.st_size,
    }

@router.post("/file")
def create_file(
    request: Request,
    body: CreateFileBody,
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()

    f = safe_path(body.path)

    if f.exists():
        if f.is_dir():
            raise HTTPException(409, detail=t(lang, "errors.dir_already_exists"))
        else:
            raise HTTPException(409, detail=t(lang, "errors.file_already_exists"))

    if not f.parent.exists():
        raise HTTPException(400, detail=t(lang, "errors.parent_not_exists"))

    try:
        f.write_text(body.content or "", encoding="utf-8")
    except Exception as e:
        # handler global converte em JSON genérico
        raise HTTPException(500, detail="errors.internal_error") from e

    return {"ok": True, "path": body.path}

@router.put("/file")
def save_file(
    request: Request,
    body: SaveBody,
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()
    f = safe_path(body.path)
    if not f.parent.exists():
        raise HTTPException(400, detail=t(lang, "errors.parent_not_exists"))

    f.write_text(body.content, encoding="utf-8")
    temp.mark_dirty(body.path, False)

    return {"ok": True}

@router.delete("/file")
def delete_path(
    request: Request,
    path: str = Query(...),
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()
    p = safe_path(path)
    if not p.exists():
        raise HTTPException(404, detail=t(lang, "errors.path_not_found"))

    if p.is_dir():
        try:
            p.rmdir()
        except OSError:
            raise HTTPException(400, detail=t(lang, "errors.dir_not_empty"))
    else:
        p.unlink()
        temp.mark_dirty(path, False)

        # 🔑 limpa também do índice de backups
        idx = load_index()
        rel_str = str(p.relative_to(BASE_DIR)).lstrip("/")
        if rel_str in idx:
            del idx[rel_str]
            save_index(idx)

        # 🔑 limpa associação de containers
        containers = load_containers()
        if rel_str in containers:
            del containers[rel_str]
            save_containers(containers)

    return {"ok": True}

# =========================================================
# Busca
# =========================================================

@router.get("/search")
def search_files(
    request: Request,
    q: str = Query(..., min_length=1),
    root: str = "",
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()
    base = safe_path(root)
    if not base.exists() or not base.is_dir():
        raise HTTPException(404, detail=t(lang, "errors.not_dir"))

    matches = []
    dirty_map = temp.load_dirty()
    for p in base.rglob("*"):
        if is_excluded_child(p):
            continue
        if q.lower() in p.name.lower():
            matches.append({
                "path": str(p.relative_to(BASE_DIR)),
                "is_dir": p.is_dir(),
                "name": p.name,
                "dirty": dirty_map.get(str(p.relative_to(BASE_DIR)), False),
            })
    return {"items": matches}

# =========================================================
# Backups
# =========================================================

@router.post("/backup")
def backup_file(
    request: Request,
    path: str = Query(...),
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()

    f = safe_path(path)
    if not f.exists() or not f.is_file():
        raise HTTPException(404, detail=t(lang, "errors.file_not_found"))

    backup_root = BASE_DIR / ".backups"
    backup_root.mkdir(parents=True, exist_ok=True)

    rel_path = f.relative_to(BASE_DIR)
    file_dir = backup_root / rel_path.parent / rel_path.stem
    file_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(settings.TZ)
    ts_date = now.strftime("%Y-%m-%d")
    ts_time = now.strftime("%H-%M-%S")
    backup_name = f"backup---{f.stem}---{ts_date}---{ts_time}{f.suffix}"
    backup_file = file_dir / backup_name

    shutil.copy2(f, backup_file)

    # 🔑 atualizar índice
    idx = load_index()
    rel_str = str(rel_path).lstrip("/")
    entry = idx.get(rel_str, [])
    entry.append(str(backup_file.relative_to(BASE_DIR)))
    idx[rel_str] = entry
    save_index(idx)

    return {"ok": True, "backup": str(backup_file.relative_to(BASE_DIR))}

@router.get("/backups")
def list_backups(
    request: Request,
    path: str = Query(...),
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()

    f = safe_path(path)
    rel_str = str(f.relative_to(BASE_DIR)).lstrip("/")

    idx = load_index()
    items = []
    for p in idx.get(rel_str, []):
        full = BASE_DIR / p
        if full.exists():
            items.append({"name": Path(p).name, "path": p})
    return {"items": items}

@router.post("/backup/restore")
def restore_backup(
    request: Request,
    file: str = Query(...),
    backup: str = Query(...),
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()

    f = safe_path(file)
    b = safe_path(backup)

    if not f.exists() or not f.is_file():
        raise HTTPException(404, detail=t(lang, "errors.file_not_found"))
    if not b.exists() or not b.is_file():
        raise HTTPException(404, detail=t(lang, "errors.file_not_found"))

    shutil.copy2(b, f)
    return {"ok": True}

@router.delete("/backup")
def delete_backup(
    request: Request,
    backup: str = Query(...),
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()

    b = safe_path(backup)
    if not b.exists() or not b.is_file():
        raise HTTPException(404, detail=t(lang, "errors.file_not_found"))

    b.unlink()

    # 🔑 remove do índice
    idx = load_index()
    for k, v in list(idx.items()):
        if backup in v:
            idx[k] = [x for x in v if x != backup]
            if not idx[k]:
                del idx[k]
            save_index(idx)
            break

    return {"ok": True}

# =========================================================
# Mover/renomear
# =========================================================

@router.post("/mv")
def move_path(
    request: Request,
    body: MoveBody,
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()

    src = safe_path(body.src)
    dst = safe_path(body.dst)

    if not src.exists():
        raise HTTPException(404, detail=t(lang, "errors.path_not_found"))

    if dst.exists():
        raise HTTPException(409, detail=t(lang, "errors.path_already_exists"))

    src_is_file = src.is_file()
    src_is_dir = src.is_dir()

    dst.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(src), str(dst))
    except Exception as e:
        raise HTTPException(400, detail=f"{t(lang, 'errors.rename_failed')}: {e}")

    # atualizar mapa dirty
    dirty_map = temp.load_dirty()
    if body.src in dirty_map:
        dirty_map[body.dst] = dirty_map.pop(body.src)
        temp.save_dirty(dirty_map)

    # atualizar temp
    tmp_dir = Path(settings.TEMP_DIR)
    old_tmp = tmp_dir / body.src
    new_tmp = tmp_dir / body.dst
    if old_tmp.exists():
        try:
            new_tmp.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_tmp), str(new_tmp))
        except Exception as e:
            logger.warning("Falha ao mover arquivo temporário %s -> %s: %s", old_tmp, new_tmp, e)

    # 🔑 atualizar índice de backups
    idx = load_index()
    src_rel = str(src.relative_to(BASE_DIR)).lstrip("/")
    dst_rel = str(dst.relative_to(BASE_DIR)).lstrip("/")

    if src_is_file:
        if src_rel in idx:
            idx[dst_rel] = idx.pop(src_rel)
    elif src_is_dir:
        keys_to_update = [key for key in list(idx.keys()) if key == src_rel or key.startswith(src_rel + "/")]
        updates = {}
        for key in keys_to_update:
            new_key = key.replace(src_rel, dst_rel, 1)
            updates[new_key] = idx[key]
        for key in keys_to_update:
            del idx[key]
        idx.update(updates)
    save_index(idx)

    # 🔑 atualizar associações de containers
    update_containers_on_move(src_rel, dst_rel, is_dir=src_is_dir)

    return {
        "ok": True,
        "src": str(src.relative_to(BASE_DIR)),
        "dst": str(dst.relative_to(BASE_DIR)),
    }

# =========================================================
# Validação
# =========================================================

@router.post("/validate")
def validate_file(
    body: SaveBody,
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()

    path = body.path
    content = body.content or ""
    ext = Path(path).suffix.lower()

    try:
        if ext in [".yaml", ".yml"]:
            import yaml
            yaml.safe_load(content)
            return {"success": True, "message": t(lang, "validate.yaml_ok")}

        elif ext == ".json":
            import json as _json
            _json.loads(content)
            return {"success": True, "message": t(lang, "validate.json_ok")}

        elif ext == ".xml":
            import xml.etree.ElementTree as ET
            ET.fromstring(content)
            return {"success": True, "message": t(lang, "validate.xml_ok")}

        elif ext == ".html":
            from html.parser import HTMLParser
            parser = HTMLParser()
            parser.feed(content)
            return {"success": True, "message": t(lang, "validate.html_ok")}

        elif ext == ".py":
            compile(content, path, "exec")
            return {"success": True, "message": t(lang, "validate.python_ok")}

        elif ext == ".ini":
            import configparser
            parser = configparser.ConfigParser()
            parser.read_string(content)
            return {"success": True, "message": t(lang, "validate.ini_ok")}

        elif ext == ".css":
            if not content.strip():
                return {"success": False, "message": t(lang, "validate.empty")}
            return {"success": True, "message": t(lang, "validate.css_ok")}

        elif ext == ".toml":
            try:
                import tomllib
                tomllib.loads(content)
            except ModuleNotFoundError:
                import toml
                toml.loads(content)
            return {"success": True, "message": t(lang, "validate.toml_ok")}

        elif ext == ".md":
            if not content.strip():
                return {"success": False, "message": t(lang, "validate.empty")}
            return {"success": True, "message": t(lang, "validate.md_ok")}

        elif ext == ".csv":
            import csv, io
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                _ = [cell for cell in row]
            return {"success": True, "message": t(lang, "validate.csv_ok")}

        else:
            if not content.strip():
                return {"success": False, "message": t(lang, "validate.empty")}
            return {"success": False, "message": t(lang, "validate.not_supported")}

    except Exception as e:
        return {"success": False, "message": t(lang, "validate.error").format(error=str(e))}

@router.post("/mkdir")
def mkdir(
    request: Request,
    body: MkdirBody,
    lang: str = None,
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    lang = lang or get_current_lang()
    d = safe_path(body.path)

    if d.exists():
        if d.is_dir():
            raise HTTPException(409, detail=t(lang, "errors.dir_already_exists"))
        else:
            raise HTTPException(409, detail=t(lang, "errors.file_already_exists"))

    try:
        d.mkdir(parents=True, exist_ok=False)
    except Exception as e:
        raise HTTPException(500, detail="errors.internal_error") from e

    return {"ok": True}
