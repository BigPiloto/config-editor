## This tutorial refers to the English language

# Editor

The **Editor** is where you view and edit files and access the main actions

![Editor closed](/documentation/images/editor_en_fechado.png)

- **File selected:** the editor opens for editing and the **top action bar** becomes available
- **Folder/Root selected:** the editor remains **closed** and the **action bar is not displayed**

![Editor open](/documentation/images/editor_en_aberto.png)

To increase or decrease the horizontal size of the tree/editor, just click and drag the divider; double-clicking it will reset to the default size

![Editor divider](/documentation/images/divisoria.png)

### Editor bottom bar

When a file is open, the editor footer displays:

- **On the left** → **file name** (with **extension**, if any)
- **In the center** → notice of **unsaved changes** when applicable (⚪ indicator also appears in the tree)
- **On the right** → **name of the associated container** or a notice indicating **no association**

![Editor bottom bar](/documentation/images/editor_bottom_bar.png)

### Editor top bar

When selecting a file, options appear:

![Editor top bar](/documentation/images/editor_top_bar.png)

### Diff

The **Diff** mode shows, side by side, the changes between the **current editor** content and the **last version saved/applied on disk**

- **Left panel:** version on disk (base) (shown at the top left)
- **Right panel:** current editor version (modified) (shown at the top right)

![Diff](/documentation/images/diff.png)

Changes are visually highlighted
- **Added** lines → addition highlight
- **Removed** lines → removal highlight
- **Modified** lines → modification highlight

> [!NOTE]
> If the `DIFF_ALLOW_EDIT` environment variable is set to `"true"`, the **right panel** (current content) remains **editable** in Diff mode
> With `"false"`, the diff is **read-only**, useful for reviewing before applying

### Actions in Differences mode

- **Return to editor** → Exits `Diff` mode`
  If `DIFF_ALLOW_EDIT` = `"true"` and you changed content during diff, **the changes remain** in the editor when returning
- **Apply disk version** → Saves the **disk version content** to the file (discards what is in the editor) and applies
- **Apply editor version** → Saves the **editor content** to the file (overwrites disk version) and applies

![Actions in diff mode](/documentation/images/actions_mode_diff.png)

> [!TIP]
> If you want to preserve the current version before applying, **create a backup** manually and then apply

### Validate

If the file **supports validation**, you can check whether the content **is valid** (e.g., syntax/format)

The check runs **on the current editor content** — no need to save first

![Validate button](/documentation/images/validate.png)

### Save file

Writes the **editor content** to disk (overwrites what is on disk) and removes the **unsaved changes** indicator (⚪)

Does not create a backup and does **not restart** the container

![Save file button](/documentation/images/save_file.png)

> [!TIP]
> Want to preserve the current version? Use `Create backup` before saving

### Download file

Downloads the **file on disk**

If there are **unsaved** changes in the editor, they will **not** be included in the download

To download recent changes, **save** first

![Download file button](/documentation/images/download_file.png)

### Create backup

Creates a backup of the **file on disk** (the currently saved version), **not** of what is in the editor

![Create backup button](/documentation/images/create_backup.png)

> [!WARNING]
> If there are **unsaved changes** in the editor, they will **not be included** in the backup

> [!TIP]
> To include your edits, **save** first and then click `Create backup`

### Manage backup

Allows you to **view** and **delete** existing backups

![Manage backups button](/documentation/images/manage_backups.png)

Clicking `Manage Backups` displays a pop-up to select the backup:

![Manage backups](/documentation/images/manage_backups_pop-up.png)

> [!NOTE]
> The default name follows the format:
> `backup---FILE_NAME---YYYY-MM-DD---HH-mm-ss.EXT`

After choosing a backup, a pop-up opens with three options:

- **View backup** → opens the **Diff** view between the **backup** and the **current editor content**
- **Delete backup** → removes the selected backup (does not affect the original file on disk)
- **Cancel** → closes the pop-up

### Diff via backup

The screen is similar to standard `Diff` mode:

![Diff backups](/documentation/images/diff_backup.png)

At the top of the editor, you will find:

- **Cancel** → return to the editor without changing the file
- **Apply backup** → saves the **backup content** to the file
- **Apply editor version** → saves the **current editor content** to the file (useful if you edited while viewing the backup diff)

> [!NOTE]
> In backup diff mode, the **left panel** shows the **Backup** and the **right panel** shows the **Editor**

> [!CAUTION]
> The backup stores **only the file content**, not the name/extension3
>
> If you changed the **extension** of the file and **apply a backup**, the content will be restored, **but the current name/extension remains**
>
> If necessary, **rename** the file after applying the backup.

### Associate container

To associate the file with a **Docker container**, click the button:

![Associate container button](/documentation/images/associate_container.png)

A pop-up will appear for you to enter the container **name** or **ID**:

![Associate container](/documentation/images/associate_container_pop-up.png)

You can **save** the association or **delete** it if you want to remove it

> [!NOTE]
> When you **rename** or **move** the file (including changing the extension), the **association is kept**

> [!TIP]
> The association enables the **`Restart` button** for that file and also displays the container’s **status** in the interface

> [!WARNING]
> For this to work, Docker integration must be enabled (socket mounted at `/var/run/docker.sock` and correct permissions)
>
> If the container is not found, the **`Restart` button** will display an error message when attempting to use the action

### Restart

Sends the **restart** command to the container **associated** with the file

![Restart container button](/documentation/images/restart.png)

When clicked, a pop-up asks for **confirmation** of the restart

> [!NOTE]
> The `Restart` button is only available when there is a **container associated** with the file


# Related Tutorials

[README](README.md)

[Getting Started](/documentation/readme/en/getting_started.md)

[After starting the container](/documentation/readme/en/container_created.md)

[Top Bar](/documentation/readme/en/top_bar.md)

[Menu](/documentation/readme/en/menu.md)

[File Tree](/documentation/readme/en/file_tree.md)

→ [Editor](/documentation/readme/en/editor.md)