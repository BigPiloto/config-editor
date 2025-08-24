## Esse tutorial é referente ao idioma Português - Brasil

# Primeiros passos

No arquivo [README-pt-BR](/documentation/readme/README-pt-BR.md) há uma explicação do que é o Config Editor e suas funcionalidades, formas de instalação e um exemplo básico de configuração para rodar o container.

Neste tutorial vamos detalhar melhor as opções de configuração disponíveis na instalação.

### Container name

Aqui você define um nome para seu container (pode ser qualquer um).

Exemplo:
``` yaml
container_name: config-editor
```

### user: "0:0"

Esse parâmetro é necessário para permitir interação com o docker.sock.

Com ele, o Config Editor consegue inspecionar containers e executar o `Reiniciar container` diretamente pela interface.

### Ports

Por padrão, o aplicativo roda na porta 5000 dentro do container.

Você pode expor essa porta em qualquer porta externa que preferir:

Exemplo:
``` yaml
ports:
  - "8080:5000"   # acessível em http://host:8080
```

### Flask secret key

Defina aqui uma chave secreta aleatória e segura, usada para criptografia de sessão.

Ela deve ser gerada pelo administrador antes de subir o container.

Exemplo de geração:
```bash
python - <<'PY'
import secrets, base64
print(base64.urlsafe_b64encode(secrets.token_bytes(48)).decode())
PY
```

### TOTP_ENABLED

Define se a autenticação em dois fatores (2FA) estará ativa no sistema.

- `true` → será necessário configurar o 2FA no primeiro login (via Google Authenticator, Authy, etc).
- `false` → o registro inicial acontece apenas com usuário e senha.

### FILE_CONTAINERS

Aqui você informa quais arquivos de configuração o editor deve gerenciar e a que container eles pertencem.

Formato:
```yaml
FILE_CONTAINERS: "arquivo.xml:nome_do_container"
```

Exemplo com múltiplos arquivos:
```yaml
FILE_CONTAINERS: "traccar.xml:traccar,tunnel.yml:cloudflared"
```

### DOCKER_HOST

Define o caminho para o socket do Docker que será usado para inspecionar e reiniciar containers.

O valor padrão é:
```perl
unix:///var/run/docker.sock
```

### DATA_DIR

Pasta usada dentro do container para leitura e escrita dos arquivos de configuração.

Exemplo de volume:
```yaml
- /srv/meus_servicos/config:/data
```

### BACKUP_DIR

Pasta usada para salvar os backups criados via interface do Config Editor.

Exemplo:
```yaml
- /srv/config-editor/backups:/backups
```

### STATE_DIR

Pasta onde ficam armazenados os dados internos do Config Editor (usuários cadastrados, segredos de 2FA, etc).

Exemplo:
```yaml
- /srv/config-editor/state:/state
```

### volumes

- /var/run/docker.sock:/var/run/docker.sock

Esse volume é obrigatório para que o Config Editor consiga se comunicar com o Docker.

Sem ele, não é possível inspecionar containers nem usar o botão Reiniciar container pela interface.

- /srv/service/config:/data

Esse volume define o local onde os arquivos de configuração do seu serviço serão acessados pelo Config Editor.

⚠️ Importante: sempre faça bind da pasta que contém os arquivos, e não de um arquivo individual.
  - ✅ Correto: /srv/service/config:/data
  - ❌ Errado: /srv/service/config/arquivo.xml:/data/arquivo.xml

Se você tiver mais de um serviço com pastas diferentes de configuração, basta mapear cada uma delas.

- /srv/config-editor/backups:/backups

Define a pasta onde os backups criados via interface serão salvos.

Mesmo que você remova ou reinicie o container, os backups continuarão disponíveis nessa pasta do host.

- /srv/config-editor/state:/state

Armazena os dados internos do Config Editor, como usuários cadastrados e chaves de autenticação (2FA).

Assim, mesmo que você remova ou recrie o container, essas informações não são perdidas.

## Opcionais do ambiente

### DEBUG (padrão: false)

Habilita ou desabilita o modo debug do Flask.

- `false` → padrão recomendado para produção.
- `true` → útil apenas para desenvolvimento/testes (mostra erros detalhados no navegador).

### DRY_RUN (padrão: false)

Controla o modo Dry-Run do Config Editor.

- `false` → as ações Salvar & Aplicar realmente gravam e aplicam as alterações.
- `true` → as alterações são validadas, mas não são aplicadas (útil para testes sem impactar os containers).

### DIFF_ALLOW_EDIT (padrão: false)

Controla se o modo de visualização de diferenças (diff view) permite ou não edições diretas.

- `false` → você pode apenas visualizar as diferenças.
- `true` → habilita a edição diretamente dentro da tela de diff.

## Tutoriais relacionados

LINK1
LINK2
