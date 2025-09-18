# backend/routes/containers.py
from fastapi import APIRouter, HTTPException, Header, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Dict, Optional
import json, logging, shlex, subprocess, re

try:
    import docker
except Exception:
    docker = None

from ..config import settings
from .deps import require_user

logger = logging.getLogger(__name__)

# Mantém a família de URLs sob /api
router = APIRouter(prefix="/api", tags=["containers"])

# Raiz do workspace
BASE_DIR = Path(getattr(settings, "DATA_DIR", "meus_arquivos")).resolve()

# Arquivo de associações arquivo⇄container
STORE_PATH = BASE_DIR / ".file_containers.json"
STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Comando para reiniciar containers
RESTART_CMD = getattr(settings, "CONTAINER_RESTART_CMD", None)

# ------------------------------- Helpers -------------------------------

def block_browser(accept: str):
    if "text/html" in (accept or "").lower():
        raise HTTPException(403, detail="errors.forbidden")

def safe_data_path(rel: str) -> Path:
    rel = (rel or "").lstrip("/")
    p = (BASE_DIR / rel).resolve()
    if BASE_DIR not in p.parents and p != BASE_DIR:
        raise HTTPException(400, detail="errors.path_outside_workspace")
    return p

def _load_store() -> Dict[str, str]:
    if STORE_PATH.exists():
        try:
            return json.loads(STORE_PATH.read_text(encoding="utf-8") or "{}")
        except Exception as e:
            logger.warning("Failed to read %s: %s", STORE_PATH, e)
            return {}
    return {}

def _save_store(data: Dict[str, str]) -> None:
    tmp = STORE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STORE_PATH)

def _inspect_state(c):
    """Retorna (status, health) em minúsculas.
    status: running|restarting|exited|created|paused|dead|...
    health: healthy|unhealthy|starting|None
    """
    try:
        c.reload()
    except Exception:
        pass
    st = (c.attrs or {}).get("State", {}) or {}
    status = str(st.get("Status") or "").lower()
    health = None
    h = st.get("Health")
    if isinstance(h, dict):
        health = str(h.get("Status") or "").lower()
    return status, health

def _container_names(c):
    """Retorna possíveis nomes sem '/'. Evita iterar string por engano."""
    names = set()
    try:
        if getattr(c, "name", None):
            names.add(c.name.lstrip("/"))
    except Exception:
        pass
    try:
        nm = c.attrs.get("Name")
        if isinstance(nm, str) and nm:
            names.add(nm.lstrip("/"))
    except Exception:
        pass
    return list(names) or [getattr(c, "name", "").lstrip("/")]


def _resolve_container(dclient, ref: str):
    """Resolve por ID (prefixo), nome exato e sufixos comuns do Compose."""
    if not ref:
        return None
    ref = ref.strip()

    # 1) ID (prefixo conta)
    try:
        # docker-py aceita ID completo; para prefixo, procure na lista
        return dclient.containers.get(ref)
    except Exception:
        pass

    # 2) varre todos (é O(n), mas lista é curta)
    try:
        allc = dclient.containers.list(all=True)
    except Exception:
        allc = []
    
    rlow = ref.lower()
    
    # (a) nome exato
    for c in allc:
        for n in _container_names(c):
            if n.lower() == rlow:
                return c

    # (b) sufixos comuns do compose
    for c in allc:
        for n in _container_names(c):
            if n.lower() in (f"{rlow}-1", f"{rlow}_1"):
                return c

    # (c) substring como último recurso
    for c in allc:
        for n in _container_names(c):
            if rlow in n.lower():
                return c

    return None

def _do_restart(container_ref: str) -> str:
    # 1) Comando externo configurado
    if RESTART_CMD:
        cmd = RESTART_CMD.format(container=container_ref)
        try:
            subprocess.run(shlex.split(cmd), check=True, capture_output=True)
            return container_ref
        except subprocess.CalledProcessError as e:
            logger.warning("Restart failed (%s): %s", container_ref, e)
            raise HTTPException(500, detail="errors.restart_failed")

    # 2) Docker SDK
    if docker is None:
        raise HTTPException(500, detail="errors.restart_not_configured")

    try:
        client = docker.from_env()
        c = _resolve_container(client, container_ref)
        if not c:
            raise HTTPException(404, detail="errors.container_not_found")

        # Inspeciona estado atual
        try:
            st = c.attrs.get("State", {}) or {}
            running = bool(st.get("Running"))
        except Exception:
            c.reload()
            running = bool((c.attrs.get("State", {}) or {}).get("Running"))

        if running:
            c.restart(timeout=getattr(settings, "DOCKER_TIMEOUT", 5))
        else:
            c.start()

        try:
            c.reload()
        except Exception:
            pass

        return c.name or container_ref
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Docker restart error: %s", e)
        raise HTTPException(500, detail="errors.restart_failed")

# ------------------------------- Schemas ------------------------------

class AssocIn(BaseModel):
    path: str = Field(..., description="Caminho relativo do arquivo")
    container: str = Field(..., min_length=1, description="Nome/ID do container")

# ------------------------------- Rotas -------------------------------

@router.get("/file/container")
async def get_file_container(
    path: str = Query(...),
    user=Depends(require_user),
    accept: str = Header(default="*/*"),
) -> Dict[str, Optional[str]]:
    block_browser(accept)
    store = _load_store()
    return {"path": path, "container": store.get(path)}

@router.put("/file/container")
async def put_file_container(
    body: AssocIn,
    user=Depends(require_user),
    accept: str = Header(default="*/*"),
) -> Dict[str, str]:
    block_browser(accept)

    try:
        file_path = safe_data_path(body.path)
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(404, detail="errors.file_not_found")

        container = body.container.strip()
        if not container:
            raise HTTPException(400, detail="errors.invalid_container")

        store = _load_store()
        store[body.path] = container
        _save_store(store)
        return {"ok": "true"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("put_file_container failed for %s -> %s", body.path, body.container)
        raise HTTPException(500, detail="errors.internal_error")

@router.delete("/file/container")
async def delete_file_container(
    path: str = Query(...),
    user=Depends(require_user),
    accept: str = Header(default="*/*"),
) -> Dict[str, str]:
    block_browser(accept)
    try:
        store = _load_store()
        if path in store:
            del store[path]
            _save_store(store)
        return {"ok": "true"}  # ← string, consistente com o PUT
    except HTTPException:
        raise
    except Exception:
        logger.exception("delete_file_container failed for %s", path)
        raise HTTPException(500, detail="errors.internal_error")

# Mapa completo (útil pro front carregar badges de uma vez)
@router.get("/containers/map")
async def get_containers_map(
    user=Depends(require_user),
    accept: str = Header(default="*/*"),
) -> Dict[str, Dict[str, str]]:
    block_browser(accept)
    return {"map": _load_store()}

# Reiniciar container associado a um arquivo (ou pelo nome/ID)
@router.post("/containers/restart")
async def restart_container(
    path: Optional[str] = Query(None, description="Arquivo associado a um container"),
    container: Optional[str] = Query(None, description="Nome ou ID do container"),
    user=Depends(require_user),
    accept: str = Header(default="*/*"),
):
    block_browser(accept)

    # 1) Descobrir o container a partir do path OU usar o nome/ID informado
    container_ref: Optional[str] = None
    if path:
        store = _load_store()
        container_ref = (store.get(path) or "").strip()
        if not container_ref:
            raise HTTPException(404, detail="errors.container_not_found")
    elif container:
        container_ref = container.strip()

    if not container_ref:
        raise HTTPException(400, detail="errors.invalid_container")

    # 2) Reiniciar via comando externo ou Docker SDK
    real_name = _do_restart(container_ref)

    # Inspecionar e responder 200 (ok) ou 202 (em progresso)
    status = health = None
    try:
        if docker is not None:
            client = docker.from_env()
            c = _resolve_container(client, real_name or container_ref)
            if c:
                status, health = _inspect_state(c)
    except Exception:
        pass
    
    payload = {
        "ok": True,
        "container": real_name or container_ref,
        "status": status,
        "health": health,
    }

    # Estados transitórios → 202
    if (status in {"restarting", "created"}) or (health == "starting"):
        return JSONResponse(payload, status_code=202)

    # Rodando e saudável → 200
    if status == "running" and (health in (None, "healthy")):
        return JSONResponse(payload, status_code=200)

    # Sem inspeção possível (ex.: RESTART_CMD externo) → considere progresso
    if status is None and health is None:
        return JSONResponse(payload, status_code=202)

    # Outros estados ainda não-ok → 202 (deixa o front continuar polling)
    return JSONResponse(payload, status_code=202)
    
# Endpoint de status (para polling do frontend)
@router.get("/containers/status")
async def container_status(
    path: Optional[str] = Query(None),
    container: Optional[str] = Query(None),
    user=Depends(require_user),
    accept: str = Header(default="*/*"),
) -> Dict[str, Optional[str]]:
    block_browser(accept)

    container_ref: Optional[str] = None
    if path:
        store = _load_store()
        container_ref = (store.get(path) or "").strip()
    elif container:
        container_ref = container.strip()

    if not container_ref:
        raise HTTPException(400, detail="errors.invalid_container")

    if docker is None:
        # Sem SDK não há inspeção; devolve desconhecido (front continua tentando se quiser)
        return {"ok": True, "container": container_ref, "status": None, "health": None}

    try:
        client = docker.from_env()
        c = _resolve_container(client, container_ref)
        if not c:
            raise HTTPException(404, detail="errors.container_not_found")
        status, health = _inspect_state(c)
        return {"ok": True, "container": c.name, "status": status, "health": health}
    except HTTPException:
        raise
    except Exception:
        logger.exception("status failed for %s", container_ref)
        raise HTTPException(500, detail="errors.internal_error")