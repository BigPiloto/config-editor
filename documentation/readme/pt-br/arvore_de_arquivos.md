## Esse tutorial é referente ao idioma Português - Brasil

# Árvore de arquivos

A árvore de arquivos Config Editor fica localizada a esquerda do editor de texto e oferece os principais comandos de manipulação da árvore de arquivos

![Árvore de arquivos](/documentation/images/arvore_de_arquivos.png)

### Nova Pasta

Cria uma nova pasta no caminho selecionado

![Botão nova pasta](/documentation/images/nova_pasta.png)

> [!TIP]
> O caminho atual pode ser visualizado no rodapé da página
>
> O campo aceita **apenas o nome**, não o caminho

> [!WARNING]
> Os botões `Nova pasta` e `Novo arquivo` só ficam habilitados ao selecionar a raiz ou uma pasta

Ao clicar no botão `Nova pasta`, será exibido um pop-up para digitar o nome da nova pasta:

![Pop up nova pasta](/documentation/images/nova_pasta_pop-up.png)

Clique em `Criar` para confirmar a criação

### Novo arquivo

Cria um novo arquivo no caminho selecionado, de forma similar à criação de pasta

![Botão novo arquivo](/documentation/images/novo_arquivo.png)

> [!TIP]
> O caminho atual pode ser visualizado no rodapé da página
>
> O campo aceita **apenas o nome**, não o caminho

> [!WARNING]
> Os botões `Nova pasta` e `Novo arquivo` só ficam habilitados ao selecionar a raiz ou uma pasta

Ao clicar no botão `Novo arquivo`, será exibido um pop-up para digitar o nome do novo arquivo:

![Pop up novo arquivo](/documentation/images/novo_arquivo_pop-up.png)

> [!WARNING]
> Ao criar um novo arquivo, lembre-se de incluir a **extensão** no nome
>
> Caso contrário, o arquivo será criado **sem extensão**
>
> Nesse caso, o sistema o tratará como **texto simples**, mas tecnicamente ele **não é `.txt`**
>
> **Exemplo correto:** `arquivo.xml` / `arquivo.txt` / `arquivo.html`

### Excluir

Exclui um arquivo ou pasta selecionado

![Botão excluir](/documentation/images/excluir.png)

> [!WARNING]
> Só é possível excluir pastas vazias, (sem arquivos ou subpastas dentro)

> [!IMPORTANT]
> No mesmo caminho, **não é permitido** existir um arquivo e uma pasta com o **mesmo nome**
>
> **Exemplo inválido**: arquivo: `teste` | pasta: `teste`
>
> **Exemplo válido**: arquivo: `teste.txt` | pasta: `teste`

### Renomear

Renomeia um arquivo ou pasta selecionada

![Botão renomear](/documentation/images/renomear.png)

> [!NOTE]
> O novo nome **não pode** ser igual ao atual **nem** duplicar outro item no **mesmo caminho**
>
> Não é possível renomear para o mesmo nome

> [!TIP]
> O campo aceita **apenas o nome**, não o caminho
>
> É possível **adicionar ou alterar a extensão** ao renomear (ex.: `config` → `config.yaml`)

### Filtro

Pesquisa por **pastas** e **arquivos** na árvore

![Filtro](/documentation/images/filtro.png)

Ao digitar, a árvore é filtrada em tempo real e os caminhos até os itens correspondentes são **automaticamente expandidos**

![Filtro ativo](/documentation/images/filtro_ativo.png)

> [!TIP]
> Ao clicar no `X`, o filtro é limpo e a árvore é **restaurada**: todas as pastas são recolhidas e fica aberto **apenas o caminho do item atualmente selecionado**

### Raiz

Ao clicar em `/..` o **diretório principal** é selecionado e **toda a árvore é recolhida**

![Raiz](/documentation/images/raiz.png)

> [!TIP]  
> Use este atalho para voltar rapidamente ao nível inicial e limpar expansões abertas

### Pastas e arquivos

- **Arquivo:** ao clicar, ele é aberto no editor **à direita**
- **Pasta:** ao clicar, ela é **selecionada e expandida**; se havia um arquivo aberto, o editor à direita é **fechado** (volta à tela inicial)

![Pasta ou arquivo selecionado na árvore](/documentation/images/arvore_selecao.png)

Para **recolher** uma pasta já aberta, clique na **seta (caret)** ao lado do nome

> [!NOTE]
> Clicar **sobre o nome** da pasta apenas **expande/seleciona** — **não** recolhe

![Seta](/documentation/images/seta.png)

### Alterações

Sempre que um arquivo tiver mudanças **não aplicadas/salvas**, ele é sinalizado com um **círculo branco (⚪)**

![Arquivo sujo](/documentation/images/sujo.png)

> [!TIP]  
> Ao **salvar** o arquivo, o indicador desaparece

### Container associado

Arquivos **associados a um container** exibem o **ícone do Docker** na árvore

![Arquivo associado](/documentation/images/docker.png)

### Alterações e container associado

Um arquivo pode ter **alterações não aplicadas** e, ao mesmo tempo, estar **associado a um container**

Nessa situação, **dois símbolos** aparecem juntos

- ⚪ Círculo branco → arquivo com **mudanças não salvas/aplicadas**
- 🐳 Ícone do Docker → arquivo **associado a container**

![Arquivo associado e sujo](/documentation/images/docker_sujo.png)

### Clique direito

Ao clicar com o botão direito do mouse em alguma pasta ou arquivo, é possível abrir um menu rápido com algumas opções

> [!NOTE]
> As opções de `Novo arquivo` e `Nova pasta` é referenciada pelo caminho do selecionado, verifique no rodapé
>
> Não é possível realizar Download de pastas, somente arquivos
