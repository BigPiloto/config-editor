# Config Editor

[🇧🇷 Read in Brazilian Portuguese](/documentation/README/README.pt-br.md)

## Overview

Config Editor is a Flask-based web application that allows you to safely edit Docker container configuration files directly from your browser.

It supports secure login, Two-Factor Authentication (2FA TOTP), manual backups, **`Save & Apply / Aplly`** to write configs, and a dedicated **`Restart container`** button.

## Features

1. ✏️ Web editor with Monaco Editor (same as VS Code).

2. 🔐 Secure login with password and 2FA (Google Authenticator, Authy, etc).

3. 💾 Manual backup in one click, with restore option.

4. 💡 Save: saves the file without applying changes.

5. ⚡ Save & Apply: saves the file and applies the configuration.

6. 🔄 Dedicated Restart container button.

7. 🛡️ Dry-Run mode for testing edits without restarting services.

8. 🌍 Multi-language support (currently English and Brazilian Portuguese).

## Installation

### Method 1: Docker Compose (Recommended)

``` yaml
version: "3.8"
services:
  app:
    image: bigpiloto/config-editor:latest
    container_name: config-editor # ------------------------------------- #1
    user: "0:0" # ------------------------------------------------------- #2
    restart: unless-stopped
    ports:
      - "5000:5000" # --------------------------------------------------- #3
    environment:
      FLASK_SECRET_KEY: "PUT_YOUR_SECRET_KEY_HERE" # -------------------- #4
      TOTP_ENABLED: true # ---------------------------------------------- #5
      FILE_CONTAINERS: "file_example.xml:container_name_of_this_file" # - #6
      DOCKER_HOST: "unix:///var/run/docker.sock" # ---------------------- #7
      DATA_DIR: /data # ------------------------------------------------- #8
      BACKUP_DIR: /backups # -------------------------------------------- #9
      STATE_DIR: /state # ----------------------------------------------- #10
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock # --------------------- #11
      - /srv/service/config:/data # ------------------------------------- #12
      - /srv/config-editor/backups:/backups # --------------------------- #13
      - /srv/config-editor/state:/state # ------------------------------- #14
```
#### Legend

1. `Container name`: choose any name you want for the container.
2. `Run as root`: required to allow interaction with docker.sock.
3. `Ports`: map port 5000 of the container to your host (UI available at http://host:5000).
4. `Flask secret key`: put a secure random key here (used for session encryption).
5. `TOTP enabled`: enable or disable two-factor authentication (2FA) in server.
6. `File containers`: map config files to the corresponding container names (file:container).
7. `Docker host`: path to Docker socket used for container management.
8. `Data directory`: where the editor reads/writes configuration files.
9. `Backup directory`: where backups created in one click are stored.
10. `State directory`: stores application state (user data, 2FA secrets, etc).
11. `Docker socket volume`: required so the app can run docker inspect and docker restart.
12. `Config volume`: bind the **`folder`** that contains your service config, not the single file.
  - If you have a single service or multiple config files in the same folder, just bind that folder:
    - ✅ `/srv/service/config:/data`
  - If you have multiple services with configs in different folders, you must bind each folder separately:
    - ✅ `/srv/service_1/config:/data`
    - ✅ `/srv/service_2/config:/data`
  - ❌ Do not bind a single file: `/srv/service/config/file_example.xml:/data/file_example.xml`
13. `Backups volume`: persistent storage for backups.
14. `State volume`: persistent storage for application state.

---
### Method 2: Docker CLI

#### Create data folders
``` bash
sudo mkdir -p /srv/service/config \
             /srv/config-editor/backups \
             /srv/config-editor/state
```

#### Generate a secret key (optional)
``` python
python - <<'PY'
import secrets, base64
print(base64.urlsafe_b64encode(secrets.token_bytes(48)).decode())
PY
```

#### Raise the container
``` bash
docker run -d --name config-editor \
  --user 0:0 \
  --restart unless-stopped \
  -p 5000:5000 \
  -e FLASK_SECRET_KEY="PUT_YOUR_SECRET_KEY_HERE" \
  -e TOTP_ENABLED=true \
  -e FILE_CONTAINERS="file_example.xml:container_name_of_this_file" \
  -e DOCKER_HOST='unix:///var/run/docker.sock' \
  -e DATA_DIR=/data \
  -e BACKUP_DIR=/backups \
  -e STATE_DIR=/state \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /srv/service/config:/data \
  -v /srv/config-editor/backups:/backups \
  -v /srv/config-editor/state:/state \
  bigpiloto/config-editor:latest
```

## Usage

## Screenshots

### Change Language UI
![Change Language UI](/documentation/images/screenshot_change_lang.png)

### Web Editor UI
![Web Editor UI](/documentation/images/screenshot_editor.png)

### Healthy Status UI
![Healthy Status UI](/documentation/images/screenshot_containers.png)

## Support & Issues

- Report bugs or suggestions at: [Issues](https://github.com/BigPiloto/config-editor/issues)

## License

This project is licensed under the MIT License - see the file [MIT License](LICENSE) for details.
manual backups, Save & Apply to write configs, and a dedicated Restart container button.
