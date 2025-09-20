## This tutorial refers to the English language

# File tree

The Config Editor file tree is located on the left side of the text editor and provides the main commands for file tree manipulation

![File tree](/documentation/images/file_tree.png)

### New folder

Creates a new folder in the selected path

![New folder button](/documentation/images/new_folder.png)

> [!TIP]
> The current path can be viewed in the footer of the page
>
> The field accepts **only the name**, not the full path

> [!WARNING]
> The `New folder` and `New file` buttons are only enabled when selecting the root or a folder

Clicking the `New folder` button will display a pop-up to enter the name of the new folder:

![New folder pop up](/documentation/images/new_folder_pop-up.png)

Click `Create` to confirm creation

### New file

Creates a new file in the selected path, similar to creating a folder

![New file button](/documentation/images/new_file.png)

> [!TIP]
> The current path can be viewed in the footer of the page
>
> The field accepts **only the name**, not the full path

> [!WARNING]
> The `New folder` and `New file` buttons are only enabled when selecting the root or a folder

Clicking the `New file` button will display a pop-up to enter the new file’s name:

![New file pop up](/documentation/images/new_file_pop-up.png)

> [!WARNING]
> When creating a new file, remember to include the **extension** in the name
>
> In that case, the system will treat it as **plain text**, but technically it **is not `.txt`**
>
> **Correct examples:** `file.xml` / `file.txt` / `file.html`

### Delete

Deletes the selected file or folder

![Delete button](/documentation/images/delete.png)

> [!WARNING]
> Only empty folders (without files or subfolders inside) can be deleted

> [!IMPORTANT]
> In the same path, it is **not allowed** to have a file and a folder with the **same name**
>
> **Invalid example**: file: `test` | folder: `test`
>
> **Valid example**: file: `test.txt` | folder: `test`

### Rename

Renames the selected file or folder

![Rename button](/documentation/images/rename.png)

> [!NOTE]
> The new name **cannot be** the same as the current one **nor** duplicate another item in the **same path**
>
> It is not possible to rename to the same name

> [!TIP]
> The field accepts **only the name**, not the full path
>
> You can **add or change the extension** when renaming (e.g., `config` → `config.yaml`)

### Filter

Searches for **folders** and **files** in the tree

![Filter](/documentation/images/filter.png)

As you type, the tree is filtered in real time and the paths to the matching items are **automatically expanded**

![Active filter](/documentation/images/active_filter.png)

> [!TIP]
> Clicking `X` clears the filter and the tree is **restored**: all folders are collapsed and **only the path of the currently selected item** remains open

### Root

By clicking `/..` the **root directory** is selected and the **entire tree is collapsed**

![Root](/documentation/images/raiz.png)

> [!TIP]
> Use this shortcut to quickly return to the top level and clear open expansions

### Folders and Files

- **File**: clicking it opens the file in the editor **on the right**
- **Folder**: clicking it **selects and expands** the folder; if a file was open, the editor on the right is **closed** (returns to the start screen)

![Folder or file selected in tree](/documentation/images/arvore_selecao.png)

To **collapse** an already open folder, click the **arrow (caret)** next to its name

> [!NOTE]
> Clicking on the **folder name** only **expands/selects** — it does not collapse

![Caret](/documentation/images/seta.png)

### Changes

Whenever a file has **unsaved/unapplied changes**, it is marked with a **white circle (⚪)**

![Dirty file](/documentation/images/sujo.png)

> [!TIP]
> When you **save** the file, the indicator disappears

### Associated Container

Files **associated with a container** display the **Docker icon** in the tree

![Associated file](/documentation/images/docker.png)

### Changes and Associated Container

A file can have **unsaved changes** and at the same time be **associated with a container**

In this situation, **two symbols** appear together:

- ⚪ White circle → file with **unsaved/unapplied changes**
- 🐳 Docker icon → file **associated with a container**

![Associated and dirty file](/documentation/images/docker_sujo.png)

### Right-click

**Right-clicking** an item in the tree (folder, file, or root) shows a **context menu** with quick actions

![Context menu](/documentation/images/context_menu.png)

The options **vary according to the type of item** selected:

- **File**
  1. `Rename`
  2. `Delete`
  3. `Download file`

- **Folder**
  1. `Rename`
  2. `Delete`
  3. `New file`
  4. `New folder`

- **Root** `(/..)`
  1. `New file`
  2. `New folder`

> [!WARNING]
> The `Delete` action for **folders** is only allowed when the folder is **empty** (no files or subfolders)

# Related Tutorials

[README](README.md)

[Getting Started](/documentation/readme/en/getting_started.md)

[After starting the container](/documentation/readme/en/container_created.md)

[Top Bar](/documentation/readme/en/top_bar.md)

[Menu](/documentation/readme/en/menu.md)

→ [File Tree](/documentation/readme/en/file_tree.md)

[Editor](/documentation/readme/en/editor.md)