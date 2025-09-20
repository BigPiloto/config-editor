## This tutorial refers to the English language

# After starting the container

As soon as the container is up, open `http://host:port`

## Language selection

You will see the initial language selection page:

![Language Selection Interface](/documentation/images/choose_lang.png)

Select the language `English` and click `Confirm`

- If the variable `TOTP_ENABLED` is set to `true` in the container configuration, you will see the registration screen with 2FA:

![Registration Interface with 2FA](/documentation/images/register_2fa.png)

1. Fill in `Username` and `Password` (and confirm the password)
2. Scan the `QR Code` in your authenticator app (Google Authenticator, Authy, etc.)
3. Enter the 6-digit code generated
4. Click `Register`

- If the variable `TOTP_ENABLED` is set to `false`, you will see the registration screen without 2FA:

![Registration Interface without 2FA](/documentation/images/register.png)

1. Fill in the `Username` and `Password` fields (and confirm the password)
2. Click `Register`

![Registration Confirmation Interface](/documentation/images/register_confirmation.png)

In both cases, a pop-up will appear indicating that the user was successfully created. Click `Go to login` to access the editor

## Ready to use

After registration, the username and password (with or without 2FA, depending on the configuration) are saved, and the web editor will already be available for use

## Login

- If the variable `TOTP_ENABLED` is set to `true` in the container configuration, you will see the login screen with 2FA

![Login Interface with 2FA](/documentation/images/login_2fa_en.png)

1. Fill in the `Username` and `Password` fields
2. Enter the 6-digit code from your authenticator app (Google Authenticator, Authy, etc.)
3. Click `Enter`

> [!IMPORTANT]
> If the user was created without 2FA (username and password only), changing the variable from `false` to `true` does not automatically enable 2FA. This only enables 2FA support on the server, allowing the user to register an authenticator app
>
> Until the authenticator app is registered, the user will continue to log in with just username and password, even with 2FA enabled on the server

- If the variable `TOTP_ENABLED` is set to `false`, you will see the login screen without 2FA:

![Login Interface withou 2FA](/documentation/images/login_en.png)

1. Fill in the `Username` and `Password` fields
2. Click `Enter`

## Editor

After login, the editor will open. To understand all its features, follow the tutorial path below

# Related Tutorials

[README](README.md)

[Getting Started](/documentation/readme/en/getting_started.md)

→ [After starting the container](/documentation/readme/en/container_created.md)

[Top Bar](/documentation/readme/en/top_bar.md)

[Menu](/documentation/readme/en/menu.md)

[File Tree](/documentation/readme/en/file_tree.md)

[Editor](/documentation/readme/en/editor.md)