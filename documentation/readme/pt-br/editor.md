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

`Voltar ao editor` → Volta ao editor, se `DIFF_ALLOW_EDIT` = `true` e foi modificado o arquivo, ao voltar ao editor, o editor fica com as modificações

`Aplicar versão em disco` → Salva e aplica o que está em disco

`Aplicar versão do editor` → Salva e aplica o que está no editor

![Ações no modo diferenças](/documentation/images/acoes_modo_diferencas.png)

### Validar



### Salvar arquivo

### Baixar arquivo

### Criar backup

### Gerenciar backup

### Associar container

### Reiniciar