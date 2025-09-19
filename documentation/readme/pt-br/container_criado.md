## Esse tutorial é referente ao idioma Português - Brasil

# Após subir o container

Assim que subir o container, abra `http://host:porta`

## Seleção de idioma

Você visualizará a página inicial de seleção de idioma:

![Interface Seleção de Idioma](/documentation/images/selecionar_idioma.png)

Selecione o idioma `Português (Brasil)` e clique em `Confirma`

- Se a variável `TOTP_ENABLED` estiver definida como `true` na configuração do container, você verá a tela de registro com o 2FA:

![Interface Registro com 2FA](/documentation/images/registro_2fa.png)

1. Preencha `Usuário` e `Senha` (e confirme a senha)
2. Escaneie o `QR Code` no app autenticador (Google Authenticator, Authy, etc)
3. Digite o código de 6 digitos gerado
4. Clique em `Registrar`

- Se a variável `TOTP_ENABLED` estiver definida como `false`, você verá a tela de registro sem o 2FA:

![Interface Registro sem 2FA](/documentation/images/registro.png)

1. Preencha os campos `Usuário` e `Senha` (e confirme a senha)
2. Clique em `Registrar`

![Interface Confirmacao de Registro](/documentation/images/confirmacao_registro.png)

Em ambos os casos irá abrir um pop-up indicando que o usuário foi criado com sucesso, clique em `Ir para o login` para acessar o editor

## Pronto para uso

Após o registro, o usuário e senha (com ou sem 2FA, conforme configurado) ficam cadastrados, e o editor web já estará disponível para uso

## Login

- Se a variável `TOTP_ENABLED` estiver definida como `true` na configuração do container, você verá a tela de login com o 2FA:

![Interface Login com 2FA](/documentation/images/login_2fa_br.png)

1. Preencha os campos `Usuário` e `Senha`
2. Digite o código de 6 digitos do seu app autenticador (Google Authenticator, Authy, etc)
3. Clique em `Entrar`

> [!IMPORTANT]
> Se o usuário foi criado sem 2FA (usuário e senha apenas), mudar a variável de `false` para `true` não ativa o 2FA automaticamente. Isso apenas habilita o suporte ao 2FA no servidor, permitindo que o usuário cadastre um aplicativo autenticador
>
>Enquanto o app autenticador não for cadastrado, o usuário continuará conseguindo acessar apenas com usuário e senha, mesmo com o 2FA ativado no servidor


- Se a variável `TOTP_ENABLED` estiver definida como `false`, você verá a tela de login sem o 2FA:

![Interface Login sem 2FA](/documentation/images/login_br.png)

1. Preencha os campos `Usuário` e `Senha`
2. Clique em `Entrar`

## Editor

Após o login, irá abrir o editor, para entender todas as funcionalidades, siga a trilha de tutoriais abaixo relacionado

# Tutoriais relacionados

[LEIA ME](/documentation/readme/README-pt-BR.md)

[Primeiros passos](/documentation/readme/pt-br/primeiros_passos.md)

→ [Após subir o container](/documentation/readme/pt-br/container_criado.md)

[Barra Superior](/documentation/readme/pt-br/barra_superior.md)

[Menu](/documentation/readme/pt-br/menu.md)

[Árvore de arquivos](/documentation/readme/pt-br/arvore_de_arquivos.md)