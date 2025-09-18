# backend/routes/__init__.py
from fastapi import APIRouter
from . import files, main, auth, settings, health, temp, containers

router = APIRouter()

# files    → operações no sistema de arquivos
router.include_router(files.router)

# temp     → operações com edições temporárias
router.include_router(temp.router)

# main     → fluxo inicial (idioma, setup, root, editor)
router.include_router(main.router)

# auth     → login/logout/setup usuário inicial
router.include_router(auth.router)

# settings → mudança de senha, usuário, 2FA
router.include_router(settings.router)

# health   → status dos containers
router.include_router(health.router)

# containers → associação arquivo ↔ container
router.include_router(containers.router)