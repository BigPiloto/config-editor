# ==========================================
# Config Editor v2 - Dockerfile (all-in-one)
# ==========================================
FROM python:3.12-slim-bookworm

# Boas práticas Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# App defaults
ENV APP_MODULE=backend.app:app \
    PORT=8000 \
    WORKERS=2 \
    THREADS=4 \
    TIMEOUT=60

# Defaults de diretórios (podem ser sobrescritos em runtime)
ENV DATA_DIR=/data \
    BACKUP_DIR=/data/.backups \
    STATE_DIR=/data/.state \
    TEMP_DIR=/data/.tmp

# Pacotes básicos + docker-ce-cli (para restart/inspect)
RUN apt-get update \
 && apt-get -y dist-upgrade \
 && apt-get install -y --no-install-recommends ca-certificates curl gnupg tzdata \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
 && chmod a+r /etc/apt/keyrings/docker.gpg \
 && . /etc/os-release \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends docker-ce-cli \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Deps Python (cache-friendly)
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install -r requirements.txt \
 && python -m pip install "gunicorn>=22.0.1" "uvicorn[standard]>=0.30"

# Copie apenas o que o app usa (NÃO copiamos config/)
COPY backend/ backend/
COPY frontend/ frontend/

# Pastas de estado/dados
RUN mkdir -p "$DATA_DIR" "$BACKUP_DIR" "$STATE_DIR" "$TEMP_DIR"

EXPOSE 8000

# Healthcheck (ajuste a rota se tiver /health)
HEALTHCHECK --interval=60s --timeout=10s --start-period=20s --retries=5 \
  CMD curl -fsS "http://127.0.0.1:${PORT}/api/readyz" || exit 1

# Em produção, use Gunicorn com worker Uvicorn
# (root para acessar /var/run/docker.sock com docker-ce-cli)
CMD ["sh", "-c", "exec gunicorn ${APP_MODULE} \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:${PORT} \
  --workers=${WORKERS} \
  --threads=${THREADS} \
  --timeout=${TIMEOUT} \
  --access-logfile=- --error-logfile=-"]
