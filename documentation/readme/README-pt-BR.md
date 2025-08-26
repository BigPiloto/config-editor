# Config Editor

[🇺🇸 Read in English](/README.md)

## Visão Geral

O Config Editor é uma aplicação web em Flask que permite editar com segurança arquivos de configuração de containers Docker diretamente pelo navegador.

Ele oferece login seguro, autenticação em dois fatores (2FA TOTP), backups manuais, a ação **`Salvar & Aplicar / Aplicar`** para atualizar configurações e um botão dedicado para **`Reiniciar container`**.

## Funcionalidades

1. ✏️ Editor web baseado no Monaco Editor (o mesmo do VS Code).

2. 🔐 Login seguro com senha e 2FA (Google Authenticator, Authy, etc).

3. 💾 Backup manual em um clique, com opção de restauração.

4. 💡 Aplicar: aplica o arquivo sem salvar um backup.

5. ⚡ Salvar & Aplicar: salva o arquivo e aplica a configuração.

6. 🔄 Botão dedicado para Reiniciar container.

7. 🛡️ Modo Dry-Run para testar alterações sem reiniciar serviços.

8. 🌍 Suporte multilíngue (atualmente Inglês e Português do Brasil).

## Instalação

### Método 1: Docker Compose (Recomendado)

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
#### Legenda

1. `Container name`: nome do container (pode ser qualquer um).
2. `Run as root (user: "0:0")`: necessário para permitir interação com o docker.sock.
3. `Ports`: expõe a porta 5000 do container no host (UI acessível em http://host:5000).
4. `Flask secret key`: insira aqui uma chave secreta aleatória e segura (usada para criptografia de sessão).
5. `TOTP Enabled true/false`: ativa ou desativa a autenticação de dois fatores (2FA) no servidor.
6. `File containers`: mapeia arquivos de configuração para os nomes dos containers (arquivo:container).
7. `Docker host`: caminho para o socket do Docker usado no gerenciamento dos containers.
8. `Data directory`: onde o editor lê e grava arquivos de configuração.
9. `Backup directory`: onde os backups criados em um clique são armazenados.
10. `State directory`: armazena o estado da aplicação (usuários, dados de 2FA, etc).
11. `Docker socket volume`: necessário para que o app execute docker inspect e docker restart.
12. `Config volume`: defina os volumes para que o container tenha acesso aos arquivos de configuração do(s) serviço(s).
  - Caso tenha apenas um serviço ou vários arquivos dentro da mesma pasta, basta mapear a pasta inteira:
    - ✅ /srv/servico/config:/data
  - Caso tenha múltiplos serviços com configurações em pastas diferentes, é necessário mapear cada arquivo individualmente:
    - ✅ /srv/servico_1/config/arquivo_1.extensao:/data/arquivo_1.extensao:rw
    - ✅ /srv/servico_1/config/arquivo_2.extensao:/data/arquivo_2.extensao:rw
    - ✅ /srv/servico_2/config/arquivo_3.extensao:/data/arquivo_3.exntesao:rw
      - ⚠️ Atenção: não use nomes duplicados em /data/, pois haverá conflito.
  - ❌ Não é permitido mapear pastas diferentes para o mesmo destino /data:
    - ❌ /srv/servico_1/config:/data
    - ❌ /srv/servico_2/config:/data
13. `Backups volume`: armazenamento persistente para backups.
14. `State volume`: armazenamento persistente para o estado da aplicação.

### Método 2: Docker CLI

#### Criar pastas de dados
``` bash
sudo mkdir -p /srv/service/config \
             /srv/config-editor/backups \
             /srv/config-editor/state
```

#### Gerar uma chave secreta (opcional)
``` python
python - <<'PY'
import secrets, base64
print(base64.urlsafe_b64encode(secrets.token_bytes(48)).decode())
PY
```

#### Executar o container
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

## Uso

→ [LEIA ME](/documentation/readme/README-pt-BR.md)

[Primeiros passos](/documentation/readme/pt-br/primeiros_passos.md)

[Após subir o container](/documentation/readme/pt-br/container_criado.md)

[Barra Superior](/documentation/readme/pt-br/barra_superior.md)

[Menu](/documentation/readme/pt-br/menu.md)

[Barra de Ações do Editor](/documentation/readme/pt-br/barra_acoes.md)

## Capturas de Tela

### Interface Trocar Idioma
![Interface Trocar Idioma](/documentation/images/screenshot_change_lang.png)

### Interface Editor Web
![Interface Editor Web](/documentation/images/screenshot_editor.png)

### Interace Status de Saúde dos Containers
![Interace Status de Saúde dos Containers](/documentation/images/screenshot_containers.png)

## Suporte & Problemas

- Relate bugs ou sugestões em: [Problemas](https://github.com/BigPiloto/config-editor/issues)

## Licença

Este projeto é licenciado sob a MIT License – veja o arquivo [MIT License](LICENSE) para mais detalhes.
