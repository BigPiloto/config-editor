## This tutorial refers to the English language

# Top Bar

The Config Editor top bar displays important information about the system and the logged-in user, as well as quick shortcuts

![Top bar](/documentation/images/top_bar.png)

## Logo and title

- CONFIG EDITOR → system identification
- Not clickable (visual use only)

![Logo and title](/documentation/images/title.png)

## Container

Shows which container is being managed according to the file selected in the file tree

Example:
- Container: traccar
- Container: cloudflared

> [!NOTE]
> Without a selected file, or if the selected file has no associated container, the default container will be displayed: `Container: config-editor` (or, if defined, the friendly name in `CONTAINER_ALIAS`)

![Container](/documentation/images/container.png)

## Status

Indicates the status of the associated container

- 🟢 Running · Healthy → container is running and healthy
- 🟡 Running · Unhealthy → container is running but has health issues
- 🔴 Stopped → container stopped
- 🔴 Error → container error

This information comes from docker inspect

![Container status](/documentation/images/status_en.png)

> [!NOTE]
> If no file is selected, or if the selected file has no associated container, the health status of the container defined in `DEFAULT_CONTAINER` will be displayed
>
> If `DEFAULT_CONTAINER` is also not defined, only `⚫` will be displayed, without reference to any container

![Container Status Error](/documentation/images/container_erro.png)

> [!TIP]
> Clicking on the Status opens a pop-up showing the state of all monitored containers (not just the current one). This allows you to get an overview of the environment directly from the interface

![Container Pop-up](/documentation/images/pop-up_containers_en.png)

Inside the pop-up there are:
- Button to `Restart` the container
- Button to `Close` the pop-up

## User

Displays the name of the logged-in user

![User](/documentation/images/user.png)

Clicking it opens a menu with options such as:

- `Editor` → returns to the main editor
- `Change username` → page to modify the username
- `Change password` → page to update the login password
- `Two-factor authentication` → page to enable or disable 2FA (TOTP)
  - This option only appears if the `TOTP_ENABLED` environment variable is set to `true`
- `Change language` → page to select another interface language

![Menu](/documentation/images/menu_en.png)

## Logout

Red button on the right corner, used to end the user session

![Logout](/documentation/images/logout.png)

# Related Tutorials

[README](README.md)

[Getting Started](/documentation/readme/en/getting_started.md)

[After starting the container](/documentation/readme/en/container_created.md)

→ [Top Bar](/documentation/readme/en/top_bar.md)

[Menu](/documentation/readme/en/menu.md)

[File Tree](/documentation/readme/en/file_tree.md)

[Editor](/documentation/readme/en/editor.md)