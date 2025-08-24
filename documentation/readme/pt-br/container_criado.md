## Esse tutorial é referente ao idioma Português - Brasil

# Após subir o container

Assim que subir o container, abra `http://host:porta`

## Seleção de idioma

Você visualizará a página inicial de seleção de idioma:

![Interface Seleção de Idioma](/documentation/images/selecionar_idioma.png)

Selecione o idioma `Português (Brasil)` e clique em `Continuar`

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

## Pronto para uso

Após o registro, o usuário e senha (com ou sem 2FA, conforme configurado) ficam cadastrados, e o editor web já estará disponível para uso.

## Tutoriais relacionados

LINK1
LINK2
