# Config Editor

[🇧🇷 Ler em Português - Brasil](/documentation/readme/README-pt-BR.md)

## Overview

Config Editor is a FastAPI-based web application that allows you to safely edit Docker container configuration files directly from your browser

It offers secure login, support for two-factor authentication (2FA TOTP), automatic backup creation whenever a change is applied, as well as the Apply action to update configurations in real time

The application also integrates with Docker, displaying the status of associated containers and providing a dedicated Restart container button

## Features

1. ✏️ Web editor based on Monaco Editor (the same as VS Code)

2. 🔐 Secure login with password and 2FA (Google Authenticator, Authy, etc.)

3. 💾 Automatic backup whenever a file is applied, with restore option

4. 💡 Apply: saves the file and automatically creates a backup of the previous version

5. 🔄 Dedicated Restart container button, directly from the browser

6. 🛡️ Diff mode with optional editing, allowing you to preview and edit differences before applying

7. 📦 Docker integration, displaying the status of associated containers

8. ⚙️ Support for DEFAULT_CONTAINER, allowing you to define a default container for unassociated files

9. 🌍 Multi-language support, currently in English and Brazilian Portuguese

## Installation

### Method 1: Docker Compose (Recommended)

```yaml
```yaml
version: "3.9"
services:
  config-editor:
    image: bigpiloto/config-editor:latest # -------------------------- #1*
    container_name: config-editor # ---------------------------------- #2*
    user: "0:0" # ---------------------------------------------------- #3
    restart: unless-stopped # ---------------------------------------- #4
    ports:
      - "8000:8000" # ------------------------------------------------ #5*
    environment:
      PORT: "8000" # ------------------------------------------------- #6
      DATA_DIR: "/data" # -------------------------------------------- #7
      TOTP_ENABLED: "true" # ----------------------------------------- #8
      SESSION_SECRET: "PUT_YOUR_SECRET_KEY_HERE" # ------------------- #9*
      HTTPS_ONLY: "false" # ------------------------------------------ #10
      TZ: "America/Sao_Paulo" # -------------------------------------- #11
      DIFF_ALLOW_EDIT: "true" # -------------------------------------- #12
      DISABLE_DOCKER_CHECKS: "false" # ------------------------------- #13
      DEFAULT_CONTAINER: "config-editor" # --------------------------- #14
      CONTAINER_ALIAS: "Config Editor" # ----------------------------- #15
    volumes:
      - caminho_host_dos_arquivos:/data # ---------------------------- #16*
      - caminho_de_pasta:/data/pasta # ------------------------------- #17
      - caminho_de_arquivo:/data/arquivo.extensão # ------------------ #18
      - caminho_dos_arquivos_de_configuração:/app/config # ----------- #19*
      - /var/run/docker.sock:/var/run/docker.sock:ro # --------------- #20

    healthcheck: 
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:8000/api/readyz || exit 1"] # - #21
      interval: 60s # ------------------------------------------------ #22
      timeout: 10s # ------------------------------------------------- #23
      retries: 5 # --------------------------------------------------- #24
      start_period: 20s # -------------------------------------------- #25

    networks:
      - cfgnet # ----------------------------------------------------- #26

networks:
  cfgnet: # ---------------------------------------------------------- #27
    external: true # ------------------------------------------------- #28
```
### Legend

* Items marked with `*` are required in docker-compose; others are optional since they already have defaults in the application

1. `image`: official application image (bigpiloto/config-editor:latest) *
2. `container_name`: container name in Docker *
    1. Can be freely changed
3. `user: "0:0"`: runs as root to allow access to docker.sock
    1. ⚠️ Recommended to keep, but can be removed if running with custom permissions
4. `restart`: automatic restart policy
    1. always, on-failure, etc
5. `ports`: port mapping *
    1. Change the left port to another available on the host
6. `PORT`: internal port used by the application
    1. ❌ Do not change (always 8000)
7. `DATA_DIR`: working directory for files
    1. Path inside the container
    2. If changed (different from /data), also update volumes
       - Example: `host_path_to_files:/custom_name`
8. `TOTP_ENABLED`: enables or disables two-factor authentication (2FA)
    1. "true" (enabled) or "false" (disabled)
9. `SESSION_SECRET`: required session key *
    1. ⚠️ Replace with a random, secret string
10. `HTTPS_ONLY`: forces HTTPS in the browser
    1. "true" (only https) or "false" (allows http)
11. `TZ`: container timezone
    1. Change according to your region
12. `DIFF_ALLOW_EDIT`: allows editing in Diff mode
    1. "true" (enabled) or "false" (view only)
13. `DISABLE_DOCKER_CHECKS`: disables automatic container checks
    1. Use "true" only if you cannot expose docker.sock
14. `DEFAULT_CONTAINER`: default container for unassociated files
    1. You can replace it with the actual name of one of your containers configured in container_name #2
15. `CONTAINER_ALIAS`: friendly name shown in the interface
    1. You can freely change it
16. `Full folder volume`: mounts an entire folder in /data *
    1. It is not allowed to map different folders to the same /data destination unless they overwrite each other
    2. If you need more files, mount them in subfolders
    3. ⚠️ Mandatory: always define a host volume for /data even if you don’t have files
        - /data is where the following are stored:
           - Edited configuration files
           - Backups (/data/.backups)
           - If you don’t map it, all this information will be lost when the container is removed or restarted
    4. Even if you only use subfolders or individual files (items 17 and 18), there must still be a main volume mounted on /data to ensure persistence
17. `Subfolder volume`: mounts only a subfolder in /data/folder
    1. There may be more than one subfolder, as long as they have different paths in the application
18. `Single file volume`: mounts a specific file in /data/file.extension
    1. There may be more than one file
19. `/app/config volume`: internal app configurations *
    1. ⚠️ Do not change the destination (/app/config), only the path on your server
    2. Essential to avoid losing language and user configuration
20. `docker.sock`: required to restart and inspect containers
    1. ⚠️ If not mounted, restart/status functions will not work
21. `test`: command executed to check if the container is healthy
    1. It calls the internal URL http://127.0.0.1:8000/api/readyz
    2. If the API does not respond, it returns an error (exit 1) and the container is marked as unhealthy
    3. ⚠️ Mandatory for the healthcheck to work
22. `interval`: how often Docker runs the healthcheck
    1. Can be adjusted (30s, 120s, etc.) depending on how much time you tolerate between checks
23. `timeout`: maximum time Docker waits for the healthcheck command to finish
    1. You can increase this if your application takes longer to respond
24. `retries`: number of consecutive failures tolerated before the container is considered unhealthy
    1. You can reduce (e.g., 3) to detect issues faster, or increase to be more tolerant
25. `start_period`: grace period right after the container starts, before healthchecks begin
    1. You can increase this if your application takes longer to start (e.g., 60s)
26. `networks`: connects the service to a Docker network
    1. Optional. If you don’t need a dedicated network, you can remove it
27. `cfgnet`: definition of the network the container will use
    1. If you don’t specify anything, Docker automatically creates a default bridge network
    2. Optional: can be removed if you don’t need a dedicated network
28. `external: true`: indicates that the network already exists in Docker and will not be created automatically by docker-compose up
    1. If you set external: true but the network doesn’t exist, Docker will throw an error
    2. If you want Compose to create the network automatically, just remove this line and leave only:
  ```yaml
  networks:
  cfgnet:
    driver: bridge
  ```

### Method 2: Docker CLI

Based on the **Dockerfile** in the project root, you can run the app with `docker build` and `docker run` without `docker-compose`

**Not recommended due to lack of data persistence**

## Usage

→ [README](README.md)

[Getting Started](/documentation/readme/en/getting_started.md)

[After starting the container](/documentation/readme/en/container_created.md)

[Top Bar](/documentation/readme/en/top_bar.md)

[Menu](/documentation/readme/en/menu.md)

[File Tree](/documentation/readme/en/file_tree.md)

[Editor](/documentation/readme/en/editor.md)

## Screenshots

### Web Editor Interface

![Interface Editor Web](/documentation/images/screenshot_editor.png)

### Container Health Status Interface

![Container Health Status Interface](/documentation/images/screenshot_containers.png)

## Support & Issues

- Report bugs or suggestions at: [Issues](https://github.com/BigPiloto/config-editor/issues)

## License

This project is licensed under the MIT License – see the [MIT License](LICENSE) file for more details
