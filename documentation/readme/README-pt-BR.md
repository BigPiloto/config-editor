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
4. Flask secret key: insira aqui uma chave secreta aleatória e segura (usada para criptografia de sessão).
5. TOTP true/false: ativa ou desativa a autenticação de dois fatores (2FA) no servidor.

File containers: mapeia arquivos de configuração para os nomes dos containers (arquivo:container).

Docker host: caminho para o socket do Docker usado no gerenciamento dos containers.

Data directory: onde o editor lê e grava arquivos de configuração.

Backup directory: onde os backups criados em um clique são armazenados.

State directory: armazena o estado da aplicação (usuários, dados de 2FA, etc).

Docker socket volume: necessário para que o app execute docker inspect e docker restart.

Config volume: faça o bind da pasta que contém as configurações do serviço, e não de um arquivo específico.

Se você tem um único serviço ou múltiplos arquivos de configuração na mesma pasta, basta mapear essa pasta:

✅ /srv/servico/config:/data

Se você tem múltiplos serviços em pastas diferentes, precisa mapear cada uma:

✅ /srv/service_1/config:/data

✅ /srv/service_2/config:/data

❌ Não faça bind de um arquivo individual: /srv/servico/config/arquivo.xml:/data/arquivo.xml

Backups volume: armazenamento persistente para backups.

State volume: armazenamento persistente para o estado da aplicação.
