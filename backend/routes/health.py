# backend/routes/health.py
from fastapi import APIRouter, Depends, Response
from pathlib import Path
from typing import Dict, List
import json, logging, os
from datetime import datetime, timezone

try:
    import docker
except Exception:
    docker = None

from ..config import settings
from .deps import require_user, browser_blocker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"])

BASE_DIR = Path(getattr(settings, "DATA_DIR", "meus_arquivos")).resolve()
STORE_PATH = BASE_DIR / ".file_containers.json"

def _load_dynamic() -> dict[str, str]:
    try:
        if STORE_PATH.exists():
            return json.loads(STORE_PATH.read_text(encoding="utf-8") or "{}")
    except Exception as e:
        logger.warning("Failed to read %s: %s", STORE_PATH, e)
    return {}

def _get_docker_client(timeout=3):
    # Permite desativar checagens de Docker via env
    if os.environ.get("DISABLE_DOCKER_CHECKS", "").lower() in ("1","true","yes","on"):
        return None
    if not docker:
        return None
    try:
        client = docker.from_env()
        try:
            client.api.timeout = getattr(settings, "DOCKER_TIMEOUT", timeout)
        except Exception:
            pass
        return client
    except Exception as e:
        logger.warning("Docker client unavailable: %s", e)
        return None

@router.get("/health")
def health_check(
    user=Depends(require_user),
    _: str = Depends(browser_blocker),
):
    # 1) une estático (.env/settings) + dinâmico (arquivo no workspace)
    static_map: Dict[str, str] = dict(getattr(settings, "FILE_CONTAINERS", {}))
    dynamic_map: Dict[str, str] = _load_dynamic()
    merged: Dict[str, str] = {**static_map, **dynamic_map}

    # 2) reorganiza em container -> [files]
    container_files: Dict[str, List[str]] = {}
    for fname, cname in merged.items():
        container_files.setdefault(cname, []).append(fname)

    default_c = os.environ.get("DEFAULT_CONTAINER")
    if default_c:
        container_files.setdefault(default_c, [])

    # 3) checagens básicas de diretórios
    temp_ok = Path(settings.TEMP_DIR).exists()
    data_ok = BASE_DIR.exists()

    # 4) docker
    docker_info = {"available": False}
    containers: Dict[str, dict] = {}
    
    client = _get_docker_client()
    if client:
        docker_info["available"] = True
        for cname, files in container_files.items():
            ok = False
            status = None
            health = None
            try:
                c = client.containers.get(cname)
                st = (getattr(c, "attrs", {}) or {}).get("State") or {}
                status = st.get("Status")
                health = (st.get("Health") or {}).get("Status")
                ok = (status == "running") and (health in (None, "healthy"))
            except Exception as e:
                logger.debug("Container inspect failed (%s): %s", cname, e)
                ok = False
            containers[cname] = {
                "ok": ok,
                "files": sorted(files),
                "status": status,
                "health": health,
            }
    else:
        # docker indisponível: ainda retornamos files mapeados
        for cname, files in container_files.items():
            containers[cname] = {
                "ok": False,
                "files": sorted(files),
                "status": None,
                "health": None,
            }

    return {
        "ok": True,
        "time": datetime.now(timezone.utc).isoformat(),
        "data_dir_ok": data_ok,
        "temp_dir_ok": temp_ok,
        "docker": docker_info,
        "containers": containers,
        "sources": {
            "static_count": len(static_map),
            "dynamic_count": len(dynamic_map),
        },
    }

@router.get("/healthz", include_in_schema=False)
def healthz():
    return {"ok": True}

@router.get("/readyz", include_in_schema=False)  # readiness público (completo)
def readyz():
    # Checks essenciais
    data_ok = BASE_DIR.exists()
    temp_ok = Path(settings.TEMP_DIR).exists()

    # Mapeamentos (arquivos associados)
    dynamic_map = _load_dynamic()
    static_map = dict(getattr(settings, "FILE_CONTAINERS", {}))
    merged = {**static_map, **dynamic_map}

    # Docker opcional (se disponível e não desabilitado)
    docker_ok = True
    containers_summary = {}
    client = _get_docker_client()
    if client:
        try:
            client.ping()
        except Exception:
            docker_ok = False

        if docker_ok and merged:
            for cname in sorted(set(merged.values())):
                status = None
                health = None
                running_ok = False
                try:
                    c = client.containers.get(cname)
                    st = (getattr(c, "attrs", {}) or {}).get("State") or {}
                    status = st.get("Status")
                    health = (st.get("Health") or {}).get("Status")
                    running_ok = (status == "running") and (health in (None, "healthy"))
                except Exception:
                    running_ok = False
                containers_summary[cname] = {
                    "status": status,
                    "health": health,
                    "ok": running_ok,
                }

    # Política de “pronto”: diretórios OK + (se docker disponível) ping OK
    all_ok = data_ok and temp_ok and (docker_ok is True)

    body = {
        "ok": all_ok,
        "data_dir_ok": data_ok,
        "temp_dir_ok": temp_ok,
        "docker_ok": docker_ok,
        "containers": containers_summary,
    }
    # 200 se pronto, 503 se não
    return (body, 200) if all_ok else (body, 503)