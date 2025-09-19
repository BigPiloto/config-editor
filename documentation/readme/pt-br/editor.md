## Esse tutorial é referente ao idioma Português - Brasil

# Editor

O **Editor** é onde você visualiza e edita arquivos e acessa as ações principais

![Editor fechado](/documentation/images/editor_br_fechado.png)

- **Arquivo selecionado:** o editor abre para edição e a **barra superior de ações** fica disponível
- **Pasta/Raiz selecionada:** o editor fica **fechado** e a **barra de ações não é exibida**

![Editor aberto](/documentation/images/editor_br_aberto.png)

### Barra inferior do editor

Quando um arquivo está aberto, o rodapé do editor exibe:

- **À esquerda** → **nome do arquivo** (com **extensão**, se houver)
- **Ao centro** → aviso de **alterações não salvas** quando aplicável (indicador ⚪ também aparece na árvore)
- **À direita** → **nome do container associado** ou um aviso indicando que **não há associação**

![Barra inferior editor](/documentation/images/barra_inferior_editor.png)

### Barra superior do editor

Ao selecionar um arquivo, opções aparecem:

![Barra superior editor](/documentation/images/barra_superior_editor.png)

### Diferenças

O modo **Diferenças** mostra, lado a lado, as mudanças entre o conteúdo **atual no editor** e a **última versão salva/aplicada em disco**

- **Painel esquerdo:** versão em disco (base) (indicado na parte superior esqeurda)
- **Painel direito:** versão atual no editor (modificada) (indicado na parte superior direita)

![Diferenças](/documentation/images/diferencas.png)

As alterações são destacadas visualmente
- Linhas **adicionadas** → realce de adição
- Linhas **removidas** → realce de remoção
- Linhas **alteradas** → realce de modificação

> [!NOTE]  
> Se a variável de ambiente `DIFF_ALLOW_EDIT` estiver como `"true"`, o **painel direito** (conteúdo atual) permanece **editável** no modo Diferenças
> Com `"false"`, o diff é **somente leitura**, útil para revisão antes de aplicar

#### Ações no modo Diferenças

- **Voltar ao editor** → Sai do modo Diferenças
  Se `DIFF_ALLOW_EDIT = "true"` e você alterou o conteúdo durante o diff, **as mudanças permanecem** no editor ao voltar
- **Aplicar versão em disco** → Grava no arquivo o **conteúdo da versão em disco** (descarta o que está no editor) e aplica
- **Aplicar versão do editor** → Grava no arquivo o **conteúdo do editor** (substitui o que está em disco) e aplica

![Ações no modo diferenças](/documentation/images/acoes_modo_diferencas.png)

> [!TIP]
> Se quiser preservar a versão atual antes de aplicar, **crie um backup** manual e só então aplique

### Validar

Se o arquivo **tiver suporte a validação**, você pode verificar se o conteúdo **está válido** (ex.: sintaxe/formato)
A verificação roda **sobre o conteúdo atual do editor** — não precisa salvar antes

![Botão validar](/documentation/images/validar.png)

### Salvar arquivo

Grava no disco o **conteúdo do editor** (substitui o que está em disco) e remove o indicador de **alterações não salvas (⚪)**
Não cria backup e **não reinicia** container

![Botão salvar arquivo](/documentation/images/salvar_arquivo.png)

> [!TIP]  
> Quer preservar a versão atual? Use **Criar backup** antes de salvar

### Baixar arquivo

Faz o download do **arquivo em disco**
Se houver alterações **não salvas** no editor, elas **não** vão no download
Para baixar as mudanças recentes, **salve** primeiro

![Botão baixar arquivo](/documentation/images/baixar_arquivo.png)

### Criar backup

Cria um backup do **arquivo em disco** (a versão atualmente salva), **não** do que está no editor

![Botão criar backup](/documentation/images/criar_backup.png)

> [!WARNING]  
> Se houver alterações **não salvas** no editor, elas **não entram** no backup

> [!TIP]  
> Para incluir suas edições, **salve** primeiro e depois clique em **Criar backup**

### Gerenciar backup

Permite **visualizar** e **excluir** backups existentes

![Botão gerenciar backups](/documentation/images/gerenciar_backups.png)

Ao clicar em `Gerenciar Backups`, é exibido um pop-up para selecionar o backup:

![Gerenciar backups](/documentation/images/gerenciar_backups_pop-up.png)

> [!NOTE]  
> O nome padrão segue o formato:  
> `backup---NOME_DO_ARQUIVO---AAAA-MM-DD---HH-mm-ss.EXT`

Após escolher um backup, abre-se um pop-up com três opções:

- **Verificar backup** → abre a visualização de **Diferenças** (diff) entre o **backup** e o **conteúdo atual do editor**
- **Excluir backup** → remove o backup selecionado (não afeta o arquivo original em disco)
- **Cancelar** → fecha o pop-up

#### Diferenças pelo backup

A tela é semelhante ao modo **Diferenças** padrão:

![Diferenças backups](/documentation/images/diferencas_backup.png)

Na parte superior do editor, você encontra:

- **Cancelar** → retorna ao editor sem alterar o arquivo
- **Aplicar backup** → grava no arquivo o **conteúdo do backup** selecionado
- **Aplicar versão do editor** → grava no arquivo o **conteúdo atual do editor** (útil se você editou algo enquanto visualizava o diff do backup)

> [!NOTE]  
> No diff de backup, o **painel esquerdo** mostra o **Backup** e o **painel direito** mostra o **Editor**

> [!CAUTION]  
> O backup armazena **apenas o conteúdo do arquivo**, não o nome/extensão  
> Se você mudou a **extensão** do arquivo e **aplicar um backup**, o conteúdo será restaurado, **mas o nome/extensão atuais permanecem**
> Caso necessário, **renomeie** o arquivo após aplicar o backup

### Associar container

Para associar o arquivo a um **container Docker**, clique no botão:

![Botão associar container](/documentation/images/associar_container.png)

Um pop-up será exibido para você informar o **nome** do container ou o **ID**:

![Associar container](/documentation/images/associar_container_pop-up.png)

Você pode **salvar** a associação ou **excluir** caso queira removê-la

> [!NOTE]  
> Ao **renomear** ou **mover** o arquivo (inclusive mudar a extensão), a **associação é mantida**

> [!TIP]  
> A associação habilita o **botão Reiniciar** para esse arquivo e também exibe o **estado** do container na interface

> [!WARNING]  
> Para funcionar, é necessário que a integração com Docker esteja ativa (socket montado em `/var/run/docker.sock` e permissões corretas)
> Se o container não for encontrado, o botão de **Reiniciar** ficará desativado e uma mensagem de erro será exibida ao tentar usar a ação

### Reiniciar

Envia o comando de **reinício** para o container **associado** ao arquivo

![Botão reiniciar container](/documentation/images/reiniciar.png)

Ao clicar, um pop-up solicita **confirmação** do reinício

> [!NOTE]  
> O botão **Reiniciar** só fica disponível quando há um **container associado** ao arquivo