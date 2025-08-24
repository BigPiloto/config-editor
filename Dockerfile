FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
 && apt-get -y dist-upgrade \
 && apt-get install -y --no-install-recommends ca-certificates curl gnupg \
 && rm -rf /var/lib/apt/lists/*

# docker-ce-cli para 'inspect' e 'restart'
RUN install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
 && chmod a+r /etc/apt/keyrings/docker.gpg \
 && . /etc/os-release \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian ${VERSION_CODENAME} stable" \
      > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends docker-ce-cli \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install -r requirements.txt \
 && python -m pip install "gunicorn>=22.0.1"

COPY backend/ /app/

RUN mkdir -p /data /backups /state

ENV DATA_DIR=/data \
    BACKUP_DIR=/backups \
    STATE_DIR=/state \
    DEBUG=false \
    DRY_RUN=false \
    TOTP_ENABLED=true \
    DIFF_ALLOW_EDIT=false \
    DEFAULT_LANG=en

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import sys,urllib.request; u=urllib.request.urlopen('http://127.0.0.1:5000/health',timeout=2); sys.exit(0 if u.getcode()==200 else 1)" || exit 1

# IMPORTANTE: sem USER => roda como root (necessário para docker.sock + docker-ce-cli)
CMD ["gunicorn", "app:create_app()", "-b", "0.0.0.0:5000", "--workers=2", "--threads=4", "--timeout=60"]
