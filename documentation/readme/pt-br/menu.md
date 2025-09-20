## Esse tutorial é referente ao idioma Português - Brasil

# Menu

O menu do usuário pode ser acessado clicando no nome de usuário exibido na barra superior

Ele contém atalhos para gerenciar informações de conta e preferências do Config Editor

![Menu](/documentation/images/menu_br.png)

### Editor

Retorna ao editor principal de arquivos de configuração

- Útil quando você está em outras páginas, como alteração de usuário, senha ou idioma

![Editor](/documentation/images/editor_br.png)

### Alterar usuário

Página para modificar o nome de usuário atual

- Requer informar a nova identificação desejada
- É necessário digitar a senha atual
- Se o 2FA estiver habilitado, também será solicitado o código TOTP
- Após salvar, o próximo login deverá ser feito com o novo usuário

![Alterar usuário](/documentation/images/alterar_usuario.png)

Passos:

1. Inserir novo nome de usuario
2. Inserir senha atual
3. Inserir o código 2FA
  - ⚠️ Esse campo só é solicitado se a autenticação de 2 fatores estiver habilitado
4. Clicar em `Alterar`

> [!TIP]
> Caso queira que o nome exibido no aplicativo de autenticação (ex.: Config Editor: usuario) seja atualizado, será necessário reescanear o QR Code disponível na tela `Autenticação de 2 fatores`

### Alterar senha

Página para atualizar a senha de login

- Requer informar a senha atual.
- É necessário digitar e confirmar a nova senha.
- Se o 2FA estiver habilitado, também será solicitado o código TOTP.
- Após salvar, o próximo login deverá ser feito com a nova senha.

![Alterar senha](/documentation/images/alterar_senha.png)

Passos:

1. Inserir senha atual
2. Inserir nova senha
3. Confirmar nova senha
4. Inserir o código 2FA
  - ⚠️ Esse campo só é solicitado se a autenticação de 2 fatores estiver habilitado
5. Clicar em `Alterar`

### Autenticação de 2 fatores

Página para habilitar ou desabilitar a autenticação de dois fatores (TOTP)

- Permite ativar a proteção com código temporário gerado por apps como Google Authenticator, Authy etc
- Mostra um QR Code que deve ser escaneado no aplicativo autenticador
- Também permite desativar o 2FA caso já esteja habilitado

> [!WARNING]
> Esse item só aparece se a variável de ambiente `TOTP_ENABLED` estiver definida como `true`

#### Ativar autenticação de 2 fatores

![Ativar 2FA](/documentation/images/ativar_2fa.png)

Passos:

1. Inserir senha atual
2. Escanear o `QR Code` com seu app autenticador
3. Inserir o código 2FA gerado
4. Clicar em `Ativar 2FA`

#### Desativar autenticação de 2 fatores

![Desativar 2FA](/documentation/images/desativar_2fa.png)

Passos:

1. Inserir senha atual
2. Inserir o código 2FA
3. Clicar em `Desativar 2FA`

### Alterar idioma

Página para selecionar o idioma da interface

- Atualmente disponível em Português (Brasil) e Inglês
- A alteração é imediata e aplicada a toda a interface, mesmo se não clicar em `Confirma`

![Alterar idioma](/documentation/images/alterar_idioma.png)

Passos:

1. Selecionar uma opção da lista
2. Clicar em `Confirma`

# Tutoriais relacionados

[LEIA ME](/documentation/readme/README-pt-BR.md)

[Primeiros passos](/documentation/readme/pt-br/primeiros_passos.md)

[Após subir o container](/documentation/readme/pt-br/container_criado.md)

[Barra Superior](/documentation/readme/pt-br/barra_superior.md)

→ [Menu](/documentation/readme/pt-br/menu.md)

[Árvore de arquivos](/documentation/readme/pt-br/arvore_de_arquivos.md)

[Editor](/documentation/readme/pt-br/editor.md)