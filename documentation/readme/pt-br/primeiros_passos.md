## Esse tutorial é referente ao idioma Português - Brasil

# Primeiros passos

No arquivo [README-pt-BR](/documentation/readme/README-pt-BR.md) há uma explicação do que é o Config Editor e suas funcionalidades, formas de instalação e um exemplo básico de configuração para rodar o container

Neste tutorial vamos detalhar melhor as opções de configuração disponíveis na instalação

### Image

Aqui define a imagem da aplicação, recomendado utilizar bigpiloto/config-editor:latest

### Container name

Aqui você define um nome para seu container (pode ser qualquer um)

Exemplo:
``` yaml
container_name: config-editor
```

### User: "0:0"

Esse parâmetro é necessário para permitir interação com o docker.sock

Com ele, o Config Editor consegue inspecionar containers e executar o `Reiniciar` diretamente pela interface

### Restart

Política de reinício automático definido no docker

* always → O Docker sempre reinicia o container, independentemente do motivo de ele ter parado
* on-failure → O Docker só reinicia o container se ele parar com erro (exit code diferente de 0)
* unless-stopped → O Docker não reinicia containers que você parou manualmente com docker stop

### Ports

Por padrão, o aplicativo roda na porta 8000 dentro do container

Você pode expor essa porta em qualquer porta externa que preferir:

Exemplo:
``` yaml
ports:
  - "8001:8000"   # acessível em http://host:8001
```

### PORT

Porta interna usada pela aplicação, não altere (sempre 8000)

### DATA_DIR

O `DATA_DIR` define onde a aplicação armazena todos os arquivos de trabalho:

- Arquivos de configuração editados
- Backups automáticos (`.backups`)
- Temporários (`.tmp`)

Por padrão é `/data`

Você pode alterar esse caminho, mas deve manter a consistência com os volumes no `docker-compose.yml`

Exemplo com o padrão:
```yaml
environment:
  DATA_DIR: "/data"
volumes:
  - /srv/config-editor/data:/data
```

### TOTP_ENABLED

Define se a autenticação em dois fatores (2FA) estará ativa no sistema

- `true` → será necessário configurar o 2FA no primeiro login (via Google Authenticator, Authy, etc).
- `false` → o registro inicial acontece apenas com usuário e senha

### SESSION_SECRET

Defina aqui uma chave secreta aleatória e segura, usada para criptografia de sessão

Ela deve ser gerada pelo administrador antes de subir o container

Exemplo de geração:
```bash
python - <<'PY'
import secrets, base64
print(base64.urlsafe_b64encode(secrets.token_bytes(48)).decode())
PY
```

### HTTPS_ONLY

Força o uso de HTTPS no navegador

- `true` → todas as requisições HTTP serão redirecionadas para HTTPS

> [!WARNING]
> É necessário que o container esteja atrás de um proxy reverso ou load balancer que forneça o certificado TLS válido (ex.: Nginx, Traefik, Caddy)

- `false` → permite acesso tanto via HTTP quanto HTTPS (recomendado apenas para ambientes de teste ou redes internas)

### TZ

Fuso horário do container, troque conforme sua região

### DIFF_ALLOW_EDIT

Controla se o modo de visualização de diferenças (diff view) permite ou não edições diretas

- `false` → você pode apenas visualizar as diferenças
- `true` → habilita a edição diretamente dentro da tela de diff

### DISABLE_DOCKER_CHECKS

Controla se o Config Editor deve ou não interagir com o Docker para verificar o estado dos containers

1. `false` (padrão) → habilita as integrações com Docker:
  - Mostra status/saúde dos containers associados
  - Permite usar o botão **Reiniciar container**
2. `true` → desativa todas as checagens e ações sobre containers
  - A interface não exibirá status nem permitirá reinício
  - Use apenas em cenários onde **não é possível montar** o volume `/var/run/docker.sock`

### DEFAULT_CONTAINER e CONTAINER_ALIAS

No Config Editor v2, você pode definir um container padrão (usado quando não há associação de arquivo) e um apelido amigável para ele:

```yaml
DEFAULT_CONTAINER: Container padrão para visualizar na barra superior quando não selecionado nenhum arquivo
CONTAINER_ALIAS: Nome amigável para essa visualização (não precisa ser igual ao default_container)
```

### Volumes

Pasta usada dentro do container para leitura e escrita dos arquivos de configuração

Exemplo de volume para montar a pasta completa:
```yaml
- /srv/meus_servicos/config:/data
```
> [!WARNING]
> Não use nomes duplicados em /data, pois haverá conflito

> [!CAUTION]
> Não é permitido mapear pastas diferentes para o mesmo destino /data para isso utilize subpastas
>
> Se foi alterado em DATA_DIR aqui tambem deve ser alterado

Exemplo alterando para outro diretório:
```yaml
volumes:
  - /srv/config-editor/data:/diretorio
```

Exemplo de volume para montar a subpasta completa:
```yaml
- /srv/meus_servicos/config:/data/config
```

Exemplo de volume para montar arquivo:
```yaml
- /srv/meus_servicos/arquivo.extensao:/data/arquivo.extensao
```
Pode haver subpastas dentro do container

> [!WARNING]
> Obrigatório sempre definir um volume do host para /data mesmo se não tiver arquivos

- É em /data que ficam salvos:
  1. Arquivos de configuração editados
  2. Backups automáticos (/data/.backups)

Se não mapear, todas essas informações serão perdidas quando o container for removido ou reiniciado

### CONFIG_DIR

Define o diretório onde ficam os **arquivos internos de configuração da aplicação**

Por padrão, é `/app/config`

Nele são armazenados:
- `lang.json` → idioma selecionado
- `user.json` → credenciais do usuário administrador inicial

> [!WARNING]
> É **obrigatório mapear esse volume para o host** se você não quiser perder idioma e usuário/senha ao recriar o container

Exemplo:
```yaml
- /srv/config-editor/config:/app/config
```

### Docker.sock

O volume do Docker socket (`/var/run/docker.sock`) permite que o Config Editor se conecte diretamente ao Docker Engine do host

Necessário para:
- Exibir status dos containers associados
- Permitir o uso do botão Reiniciar

> [!NOTE]
> Se não montar, o Config Editor funcionará apenas como editor de arquivos

Nesse caso, use também:
```yaml
DISABLE_DOCKER_CHECKS: "true"
```

### Test

Define o comando que o Docker executa para verificar se o container está saudável

Se a API não responder, retorna erro (exit 1) e o container é marcado como unhealthy

> [!IMPORTANT]
> Obrigatório para o healthcheck funcionar

### Interval

Frequência com que o Docker executa o healthcheck

Pode ajustar (30s, 120s, etc) dependendo de quanto tempo tolera entre verificações

### Timeout

Tempo máximo que o Docker espera o comando do healthcheck terminar

Pode aumentar se sua aplicação demorar para responder

### Retries

Quantas falhas consecutivas são toleradas antes do container ser considerado unhealthy

Pode reduzir (ex: 3) para detectar mais rápido, ou aumentar para ser mais tolerante

### Start Period

Período de carência logo após o container iniciar, antes de começar a checar saúde

Pode aumentar se sua aplicação demorar mais para iniciar (ex: 60s)

### Networks

Conecta o serviço a uma rede Docker

Opcional. Se não precisa de rede dedicada, pode remover


# Tutoriais relacionados

[LEIA ME](/documentation/readme/README-pt-BR.md)

→ [Primeiros passos](/documentation/readme/pt-br/primeiros_passos.md)

[Após subir o container](/documentation/readme/pt-br/container_criado.md)

[Barra Superior](/documentation/readme/pt-br/barra_superior.md)

[Menu](/documentation/readme/pt-br/menu.md)

[Árvore de arquivos](/documentation/readme/pt-br/arvore_de_arquivos.md)