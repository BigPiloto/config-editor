## This tutorial refers to the English language

# Editor Action Bar

The Config Editor action bar is located above the text editor and provides the main commands for managing configuration files.

![Action Bar](/documentation/images/action_bar.png)

### File

Dropdown menu listing the files configured in the **FILE_CONTAINERS** parameter.

- Allows you to choose which configuration file will be opened and edited.
- When switching files, the corresponding content is loaded into the editor.

![File](/documentation/images/file.png)

### Save & Apply

- Saves the edited content and immediately applies the change to the linked container.
- Also creates a backup before applying the modification.

![Save & Apply](/documentation/images/save_apply.png)

### Apply

- Applies the edited content to the container without creating a backup.
- Useful for quick changes during testing, but less safe.

![Apply](/documentation/images/apply.png)

### Restart container

- Restarts the container linked to the selected file.
- Can be used after major configuration changes.

![Restart container](/documentation/images/restart_container.png)

### Validate

- Performs syntactic and structural validation of the configuration file.
- Supports YAML (.yaml, .yml) and XML (.xml).
- In case of errors, it shows the line/column and error message; no changes are applied to the file.

![Validate](/documentation/images/validate.png)

### Diff

- Shows a comparison (diff) between the current content in the editor and what is saved in the file.
- Useful for reviewing changes before applying.
- If `DIFF_ALLOW_EDIT=true`, it is also possible to edit directly in diff mode.

![Diff](/documentation/images/diff.png)

![Editor Diff](/documentation/images/editor_diff.png)

### Return to Editor

- Botão exibido apenas quando o modo Diferenças (diff) está ativo.
- Enquanto o diff está aberto, os demais botões da barra de ações (Salvar e Aplicar, Aplicar, Reiniciar container, Validar, Versões, Excluir) ficam desabilitados.
- Serve para retornar ao editor normal, onde todas as ações voltam a ficar disponíveis.
- O conteúdo no editor permanece exatamente como estava antes de abrir o diff.

![Return to Editor](/documentation/images/return_editor.png)

### Versions

- Lists the backup versions of the file.
- When selecting a version, it is loaded into the editor.
- To write it to the current file, you must click `Save & Apply` or `Apply`.

![Versions](/documentation/images/versions.png)

![Versions List](/documentation/images/versions_menu.png)

### Delete

- Allows you to delete a previously created backup version.
- ⚠️ You must select a backup from the versions list in order to delete it.
- ❌ It is not possible to delete the file currently in use.
- If you want to completely remove a file from Config Editor, you must edit the docker-compose.yml (`FILE_CONTAINERS` variable).

![Delete](/documentation/images/delete.png)

# Related Tutorials

LINK1
LINK2
