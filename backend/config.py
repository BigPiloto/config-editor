import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).with_name(".env")
RUNNING_IN_DOCKER = Path("/.dockerenv").exists()
if ENV_PATH.exists() and not RUNNING_IN_DOCKER:
  load_dotenv(ENV_PATH, override=False)

# --- helpers ---
def _b(env_name: str, default: bool = False) -> bool:
  """Converte variável de ambiente em boolean."""
  return os.environ.get(env_name, str(default)).strip().lower() in ("1", "true", "yes", "on")

class Settings:
  # Diretórios (padrões para rodar no container com volume /data)
  DATA_DIR   = os.environ.get("DATA_DIR", "/data")
  BACKUP_DIR = os.environ.get("BACKUP_DIR", os.path.join(DATA_DIR, "backups"))
  STATE_DIR  = os.environ.get("STATE_DIR",  os.path.join(DATA_DIR, ".state"))

  # Execução
  FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "change-me")
  DEBUG = _b("DEBUG", False)

  # Modo aplicação
  DRY_RUN = _b("DRY_RUN", False)
  TOTP_ENABLED = _b("TOTP_ENABLED", True)

  # Mapa de arquivos → containers (ex.: "traccar.xml:traccar,tunnel.yml:cloudflared")
  FILE_CONTAINERS: dict[str, str] = {}
  _raw = os.environ.get("FILE_CONTAINERS", "")
  for pair in _raw.split(","):
    pair = pair.strip()
    if not pair or ":" not in pair:
      continue
    fname, cname = [p.strip() for p in pair.split(":", 1)]
    if fname and cname:
      FILE_CONTAINERS[fname] = cname

  # Comportamento do Diff
  # true = aplicar edições ao voltar. false = bloquear edição
  DIFF_ALLOW_EDIT = _b("DIFF_ALLOW_EDIT", False)

  # Idioma
  DEFAULT_LANG = "en"
  SUPPORTED_LANGS = ["en", "pt-BR"]

settings = Settings()
