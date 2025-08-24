## This tutorial refers to the English language

# After starting the container

Once the container is up and running, open in your browser `http://host:port`

## Language selection

You will see the initial language selection page:

![Language Selection Interface](/documentation/images/select_lang.png)

Select the language `English` and click `Continue`

- If the `TOTP_ENABLED` variable is set to `true` in the container configuration, you will see the registration screen with 2FA:

![Registration Interface with 2FA](/documentation/images/register_2fa.png)

1. Fill in `Username` and `Password` (and confirm the password)
2. Scan the `QR Code` with an authenticator app (Google Authenticator, Authy, etc)
3. Enter the generated 6-digit code
4. Click `Register`

- If the TOTP_ENABLED variable is set to false, you will see the registration screen without 2FA:

![Registration Interface without 2FA](/documentation/images/register.png)

1. Fill in `Username` and `Password` (and confirm the password)
2. Click `Register`

## Ready to use

After registration, the username and password (with or without 2FA, depending on the configuration) are saved, and the web editor is ready for use.

# Related tutorials

[READ ME](/README.md)

[Getting Started](/documentation/readme/en/getting_started.md)

→ [After starting the container](/documentation/readme/en/container_created.md)

[Top Bar](/documentation/readme/en/top_bar.md)

[User Menu](/documentation/readme/en/menu.md)

[Editor Action Bar](/documentation/readme/en/actions_bar.md)
