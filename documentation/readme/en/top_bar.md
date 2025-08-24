## This tutorial refers to the English language

# Top Bar

The top bar of Config Editor displays important information about the system and the logged-in user, as well as quick shortcuts.

![Top Bar](/documentation/images/top_bar.png)

## Logo and Title

- CONFIG EDITOR → system identification.
- Not clickable (visual use only).

![Logo and Title](/documentation/images/logo_e_titulo.png)

## Mode

Displays the current operating mode defined in the container:

- PRODUCTION → default mode, used in real environments.
- DRY-RUN → if enabled, changes can be made and previewed, but will not be applied to the container.

This setting is controlled by the environment variable DRY_RUN.

![Mode](/documentation/images/mode.png)

## Container

Shows which container is being managed according to the file selected in `File`:.

Example:
- Container: traccar
- Container: cloudflared

If you have multiple files, you can switch between them through the editor in `File`:.

If not defined in FILE_CONTAINERS, it will appear as `Container: Not defined`.

![Container](/documentation/images/container.png)

## Status

Indicates the status of the associated container:

- 🟢 Running · Healthy → container is running and healthy.
- 🟡 Running · Unhealthy → container is running but has health issues.
- 🔴 Stopped → container is stopped.
- 🔴 Error → container has an error.

This information comes from docker inspect.

![Container Status](/documentation/images/status_en.png)

👉 By clicking on Status, a pop-up opens showing the state of all monitored containers (not just the current one). This provides an overview of the environment directly through the interface.

![Container Pop-up](/documentation/images/pop-up_containers_en.png)

## User

Displays the name of the logged-in user.

![User](/documentation/images/usuario.png)

Clicking it opens a menu with options such as:

- `Editor` → returns to the main editor.
- `Change user` → page to modify the username.
- `Change password` → page to update the login password.
- `Two-Factor Authentication` → page to enable or disable 2FA (TOTP).
  - ⚠️ This option only appears if the environment variable **TOTP_ENABLED** is set to `true`.
- `Change Language` → page to switch the interface language.

![Menu](/documentation/images/menu_en.png)

## Logout

Red button in the top-right corner, used to end the user session.

![Logout](/documentation/images/logout.png)

# Related tutorials

[READ ME](README.md)

[Getting Started](/documentation/readme/en/getting_started.md)

[After starting the container](/documentation/readme/en/container_created.md)

→ [Top Bar](/documentation/readme/en/top_bar.md)

[User Menu](/documentation/readme/en/menu.md)

[Editor Action Bar](/documentation/readme/en/actions_bar.md)
