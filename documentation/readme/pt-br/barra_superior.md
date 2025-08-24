## Esse tutorial é referente ao idioma Português - Brasil

# Barra Superior

A barra superior do Config Editor exibe informações importantes sobre o sistema e o usuário logado, além de atalhos rápidos.

![Barra Superior](/documentation/images/barra_superior.png)

## Logo e título

- CONFIG EDITOR → identificação do sistema.
- Não é clicável (uso apenas visual).

![Logo e Título](/documentation/images/logo_e_titulo.png)

## Mode

Exibe o modo atual de operação definido no container:

- PRODUÇÃO → modo padrão, usado em ambiente real.
- DRY-RUN → se habilitado, as alterações podem ser feitas e visualizadas, mas não são aplicadas no container.

Essa configuração é controlada pela variável de ambiente DRY_RUN.

![Modo](/documentation/images/modo.png)

## Container

Mostra qual container está sendo gerenciado de acordo com o arquivo selecionado em `Arquivo:`.

Exemplo:
- Container: traccar
- Container: cloudflared

Se você tiver múltiplos arquivos, poderá alternar entre eles pelo editor em `Arquivo:`.

Se não for definido em FILE_CONTAINERS aparecerá como `Container: Não definido`.

![Container](/documentation/images/container.png)

## Status

Indica a situação do container associado:

- 🟢 Em execução · Saudável → container em execução e saudável.
- 🟡 Em execução · Doente → container em execução, mas com problemas de saúde.
- 🔴 Parado → container parado.
- 🔴 Erro → Erro no container.

Essa informação vem do docker inspect.

![Status do Container](/documentation/images/status_pt.png)

👉 Ao clicar no Status, é aberto um pop-up mostrando o estado de todos os containers monitorados (não apenas o atual). Isso permite ter uma visão geral do ambiente diretamente pela interface.

![Pop-up do Container](/documentation/images/pop-up_containers_pt.png)

## Usuário

Exibe o nome do usuário logado.

![Usuário](/documentation/images/usuario.png)

Ao clicar, abre um menu com opções como:

- `Editor` → retorna ao editor principal.
- `Alterar usuário` → página para modificar o nome de usuário.
- `Alterar senha` → página para atualizar a senha de login.
- `Autenticação de 2 fatores` → página para habilitar ou desabilitar o 2FA (TOTP).
  - ⚠️ Essa opção só aparece se a variável de ambiente **TOTP_ENABLED** estiver definida como `true`.
- `Altera idioma` → página para selecionar outro idioma da interface.

![Menu](/documentation/images/menu_pt.png)

## Logout

Botão vermelho no canto direito, usado para encerrar a sessão do usuário.

![Sair](/documentation/images/sair.png)

# Tutoriais relacionados

[LEIA ME](/documentation/readme/README-pt-BR.md)

[Primeiros passos](/documentation/readme/pt-br/primeiros_passos.md)

[Após subir o container](/documentation/readme/pt-br/container_criado.md)

→ [Barra Superior](/documentation/readme/pt-br/barra_superior.md)

[Menu](/documentation/readme/pt-br/menu.md)

[Barra de Ações do Editor](/documentation/readme/pt-br/barra_acoes.md)
