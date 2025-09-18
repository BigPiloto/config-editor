# backend/routes/temp.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pathlib import Path
from typing import Optional
import os
import json

from ..config import settings
from .deps import require_user, browser_blocker

# Mantém as mesmas URLs finais (/api/temp, /api/dirty)
router = APIRouter(prefix="/api", tags=["temp"])

# garante que exista a pasta temporária
os.makedirs(settings.TEMP_DIR, exist_ok=True)

TEMP_ROOT = Path(settings.TEMP_DIR).resolve()
DIRTY_FILE = TEMP_ROOT / ".dirty.json"

# ------------------------
# Helpers
# ------------------------
def safe_tmp(rel: str) -> Path:
    rel = (rel or "").lstrip("/")
    p = (TEMP_ROOT / rel).resolve()
    if TEMP_ROOT not in p.parents and p != TEMP_ROOT:
        raise HTTPException(400, detail="errors.path_outside_workspace")
    return p

def load_dirty() -> dict:
    if DIRTY_FILE.exists():
        try:
            return json.loads(DIRTY_FILE.read_text(encoding="utf-8") or "{}")
        except Exception:
            return {}
    return {}

def save_dirty(data: dict):
    DIRTY_FILE.parent.mkdir(parents=True, exist_ok=True)
    DIRTY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def mark_dirty(path: str, is_dirty: bool):
    data = load_dirty()
    if is_dirty:
        data[path] = True
    else:
        data.pop(path, None)
    save_dirty(data)

# ------------------------
# Rotas
# ------------------------
@router.put("/temp")
async def save_temp(
    request,
    path: Optional[str] = Query(None),
    content: Optional[str] = Query(None),
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    body = {}
    ct = (request.headers.get("content-type") or "").lower()
    if "application/json" in ct:
        try:
            body = await request.json()
        except Exception:
            body = {}
    path = path or body.get("path")
    content = content if content is not None else body.get("content", "")
    if not path:
        raise HTTPException(400, detail="errors.missing_path")

    temp_path = safe_tmp(path)

    # se já existe uma pasta nesse caminho, não pode salvar como arquivo
    if temp_path.exists() and temp_path.is_dir():
        raise HTTPException(400, detail="errors.path_is_directory")

    temp_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path.write_text(content or "", encoding="utf-8")

    # marca como dirty
    mark_dirty(path, True)
    return {"ok": True, "path": str(temp_path.relative_to(TEMP_ROOT))}

@router.get("/temp")
async def get_temp(
    path: str = Query(...),
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    temp_path = safe_tmp(path)

    if temp_path.exists() and temp_path.is_file():
        return {"exists": True, "content": temp_path.read_text(encoding="utf-8")}

    # se for pasta ou não existir, responde vazio
    return {"exists": False}

@router.delete("/temp")
async def delete_temp(
    path: str = Query(...),
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    temp_path = safe_tmp(path)

    if temp_path.exists() and temp_path.is_file():
        temp_path.unlink()

    mark_dirty(path, False)
    return {"ok": True, "path": path}

@router.get("/dirty")
async def get_dirty_route(
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    return {"dirty": load_dirty()}

@router.delete("/dirty")
async def clear_dirty(
    path: str = Query(...),
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    mark_dirty(path, False)
    return {"ok": True, "path": path}