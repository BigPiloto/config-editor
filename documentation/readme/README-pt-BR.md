# Config Editor

[🇺🇸 Read in English](/README.md)

## Visão Geral

O Config Editor é uma aplicação web em FastAPI que permite editar com segurança arquivos de configuração de containers Docker diretamente pelo navegador

Ele oferece login seguro, suporte a autenticação em dois fatores (2FA TOTP), criação automática de backups sempre que uma alteração é aplicada, além da ação Aplicar para atualizar configurações em tempo real

A aplicação também se integra ao Docker, exibindo o estado dos containers associados e fornecendo um botão dedicado para Reiniciar container

## Funcionalidades

1. ✏️ Editor web baseado no Monaco Editor (o mesmo do VS Code)

2. 🔐 Login seguro com senha e 2FA (Google Authenticator, Authy, etc)

3. 💾 Backup automático sempre que um arquivo é aplicado, com opção de restauração

4. 💡 Aplicar: aplica o arquivo e gera automaticamente um backup da versão anterior

5. 🔄 Botão dedicado para Reiniciar container, diretamente pelo navegador

6. 🛡️ Modo Diff com edição opcional, permitindo visualizar e editar diferenças antes de aplicar

7. 📦 Integração com Docker, exibindo status de containers associados

8. ⚙️ Suporte ao DEFAULT_CONTAINER, permitindo definir um container padrão para arquivos sem associação

9. 🌍 Suporte multilíngue, atualmente em Inglês e Português do Brasil

## Instalação

### Método 1: Docker Compose (Recomendado)

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
### Legenda

* Itens com `*` são obrigatórios definir no docker-compose, demais são opcionais, uma vez que já tem definido no padrão da aplicação

1. `image`: imagem oficial da aplicação (bigpiloto/config-editor:latest) *
2. `container_name`: nome do container no Docker *
    1. Pode alterar livremente
3. `user: "0:0"`: executa como root para permitir acesso ao docker.sock
    1. ⚠️ Recomendado manter, mas pode remover se rodar com permissões customizadas
4. `restart`: política de reinício automático
    1. always, on-failure, etc
5. `ports`: mapeamento de portas *
    1. Troque a porta da esquerda para outra disponível no host
6. `PORT`: porta interna usada pela aplicação
    1. ❌ Não altere (sempre 8000)
7. `DATA_DIR`: diretório de trabalho dos arquivos
    1. Caminho do diretório dentro do container
    2. Se alterado (diferente de /data) também trocar nos volumes
       - Exemplo: `caminho_host_dos_arquivos:/nome_alterado`
8. `TOTP_ENABLED`: ativa ou desativa a autenticação de dois fatores (2FA) no servidor
    1. "true" (habilitado) ou "false" (desabilitado)
9. `SESSION_SECRET`: chave obrigatória para sessão *
    1. ⚠️ Troque por uma string aleatória e secreta
10. `HTTPS_ONLY`: força HTTPS no navegador
    1. "true" (somente https) ou "false" (permite http)
11. `TZ`: fuso horário do container
    1. Troque conforme sua região
12. `DIFF_ALLOW_EDIT`: permite editar no modo Diff
    1. "true" (habilitado) ou "false" (somente visualização)
13. `DISABLE_DOCKER_CHECKS`: desativa verificações automáticas de containers
    1. Só use "true" se não puder expor o docker.sock
14. `DEFAULT_CONTAINER`: container padrão quando um arquivo não tem associação
    1. Pode trocar pelo nome real de um container seu configurado em container_name #2
15. `CONTAINER_ALIAS`: nome amigável exibido na interface
    1. Pode trocar livremente
16. `Volume de pasta inteira`: monta uma pasta completa em /data *
    1. Não é permitido mapear pastas diferentes para o mesmo destino /data se não sobreescreve
    2. Se precisar de mais arquivos, monte em subpastas
    3. ⚠️ Obrigatório: sempre defina um volume do host para /data mesmo se não tiver arquivos
        - É em /data que ficam salvos:
           - Arquivos de configuração editados
           - Backups automáticos (/data/.backups)
           - Se não mapear, todas essas informações serão perdidas quando o container for removido ou reiniciado
    4. Mesmo que você utilize apenas subpastas ou arquivos individuais (itens 17 e 18), ainda assim deve existir um volume principal montado em /data para garantir persistência
17. `Volume de subpasta`: monta apenas uma subpasta em /data/pasta
    1. Pode haver mais de uma subpasta, desde que caminho diferente na aplicação
18. `Volume de arquivo único`: monta um arquivo específico em /data/arquivo.extensão
    1. Pode haver mais de um arquivo
19. `/app/config volume`: configurações internas do app *
    1. ⚠️ Não altere o destino (/app/config) somente o caminho no seu servidor
    2. Essencial para não perder a linguagem e a configuração de usuário
20. `docker.sock`: necessário para reiniciar e inspecionar containers
    1. ⚠️ Se não montar, funções de reinício/status não funcionarão.
21. `test`: Comando que será executado para verificar se o container está saudável
    1. Aqui ele chama a URL interna http://127.0.0.1:8000/api/readyz
    2. Se a API não responder, retorna erro (exit 1) e o container é marcado como unhealthy
    3. ⚠️ Obrigatório para o healthcheck funcionar
22. `interval`: Frequência com que o Docker executa o healthcheck
    1. Pode ajustar (30s, 120s, etc) dependendo de quanto tempo tolera entre verificações
23. `timeout`: Tempo máximo que o Docker espera o comando do healthcheck terminar
    1. Pode aumentar se sua aplicação demorar para responder
24. `retries`: Quantas falhas consecutivas são toleradas antes do container ser considerado unhealthy
    1. Pode reduzir (ex: 3) para detectar mais rápido, ou aumentar para ser mais tolerante
25. `start_period`: Período de carência logo após o container iniciar, antes de começar a checar saúde
    1. Pode aumentar se sua aplicação demorar mais para iniciar (ex: 60s)
26. `networks`: conecta o serviço a uma rede Docker
    1. Opcional. Se não precisa de rede dedicada, pode remover
27. `cfgnet`: definição da rede que o container vai usar
    1. Se você não especificar nada, o Docker cria automaticamente uma rede bridge padrão
    2. Opcional: pode remover se não precisar de rede dedicada
28. `external: true`: indica que a rede já existe no Docker e não será criada automaticamente pelo docker-compose up
    1. Se deixar external: true mas a rede não existir, o Docker vai dar erro
    2. Se quiser que o Compose crie a rede automaticamente, basta remover essa linha e deixar apenas
  ```yaml
  networks:
  cfgnet:
    driver: bridge
  ```

### Método 2: Docker CLI

Conforme **Dockerfile** na raiz do projeto, é possível rodar a aplicação com `docker build` e `docker run` sem precisar de `docker-compose`

**Não recomendado devido a não persistência de dados**

## Uso

→ [LEIA ME](/documentation/readme/README-pt-BR.md)

[Primeiros passos](/documentation/readme/pt-br/primeiros_passos.md)

[Após subir o container](/documentation/readme/pt-br/container_criado.md)

[Barra Superior](/documentation/readme/pt-br/barra_superior.md)

[Menu](/documentation/readme/pt-br/menu.md)

[Árvore de arquivos](/documentation/readme/pt-br/arvore_de_arquivos.md)

## Capturas de Tela

### Interface Editor Web
![Interface Editor Web](/documentation/images/screenshot_editor.png)

### Interace Status de Saúde dos Containers
![Interace Status de Saúde dos Containers](/documentation/images/screenshot_containers.png)

## Suporte & Problemas

- Relate bugs ou sugestões em: [Problemas](https://github.com/BigPiloto/config-editor/issues)

## Licença

Este projeto é licenciado sob a MIT License – veja o arquivo [MIT License](LICENSE) para mais detalhes.