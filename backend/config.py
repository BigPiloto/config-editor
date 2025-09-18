# backend/config.py
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timezone
import zoneinfo

# carregar variáveis do .env
load_dotenv()

# --- helpers ---
def _b(env_name: str, default: bool = False) -> bool:
    """Converte variável de ambiente em boolean."""
    return os.environ.get(env_name, str(default)).strip().lower() in ("1", "true", "yes", "on")

class Settings:
    def __init__(self):
        # Diretórios principais
        # Observação: mantive default de DATA_DIR como "/data" para compatibilidade com Docker.
        self.DATA_DIR = os.environ.get("DATA_DIR", "/data")
        self.BACKUP_DIR = os.environ.get("BACKUP_DIR", os.path.join(self.DATA_DIR, ".backups"))
        self.STATE_DIR = os.environ.get("STATE_DIR", os.path.join(self.DATA_DIR, ".state"))
        self.TEMP_DIR = os.environ.get("TEMP_DIR", os.path.join(self.DATA_DIR, ".tmp"))

        # Diretório e arquivos de configuração (centralizados)
        cfg_dir = Path(os.environ.get("CONFIG_DIR", "config")).resolve()
        cfg_dir.mkdir(parents=True, exist_ok=True)
        self.CONFIG_DIR: Path = cfg_dir

        lang_file_env = os.environ.get("LANG_FILE")
        user_file_env = os.environ.get("USER_FILE")
        
        self.LANG_FILE: Path = Path(lang_file_env) if lang_file_env else (cfg_dir / "lang.json")
        self.USER_FILE: Path = Path(user_file_env) if user_file_env else (cfg_dir / "user.json")

        # garante que as pastas dos arquivos existam (caso LANG_FILE/USER_FILE sejam caminhos absolutos customizados)
        self.LANG_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.USER_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Sessão
        self.SESSION_SECRET = os.environ.get("SESSION_SECRET", "change-me")

        # Segurança
        self.TOTP_ENABLED = _b("TOTP_ENABLED", True)
        self.HTTPS_ONLY = _b("HTTPS_ONLY", False)

        # Containers associados a arquivos
        self.FILE_CONTAINERS: dict[str, str] = {}
        _raw = os.environ.get("FILE_CONTAINERS", "")
        for pair in _raw.split(","):
            pair = pair.strip()
            if not pair or ":" not in pair:
                continue
            fname, cname = [p.strip() for p in pair.split(":", 1)]
            if fname and cname:
                self.FILE_CONTAINERS[fname] = cname

        # Comando opcional para reiniciar containers e timeout do Docker (usados em routes/containers.py e health.py)
        self.CONTAINER_RESTART_CMD = os.environ.get("CONTAINER_RESTART_CMD") or None
        try:
            self.DOCKER_TIMEOUT = int(os.environ.get("DOCKER_TIMEOUT", "3"))
        except Exception:
            self.DOCKER_TIMEOUT = 3

        # Comportamento do Diff
        self.DIFF_ALLOW_EDIT = _b("DIFF_ALLOW_EDIT", False)

        # Idiomas
        self.DEFAULT_LANG = "en"
        self.SUPPORTED_LANGS = ["en", "pt-BR"]

        # Timezone
        self.TZ_NAME = os.environ.get("TZ", "UTC")
        try:
            self.TZ = zoneinfo.ZoneInfo(self.TZ_NAME)
        except Exception:
            self.TZ = timezone.utc  # fallback
            self.TZ_NAME = "UTC"

# Instância global
settings = Settings()