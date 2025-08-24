## Esse tutorial é referente ao idioma Português - Brasil

# Barra de Ações do Editor

A barra de ações do Config Editor fica localizada acima do editor de texto e oferece os principais comandos de manipulação dos arquivos de configuração.

![Barra de Ações](/documentation/images/barra_acoes.png)

### Arquivo

Menu suspenso que lista os arquivos configurados no parâmetro **FILE_CONTAINERS**.

- Permite escolher qual arquivo de configuração será aberto e editado.
- Ao trocar de arquivo, o conteúdo correspondente é carregado no editor.

![Arquivo](/documentation/images/arquivo.png)

### Salvar & Aplicar

- Salva o conteúdo editado e aplica imediatamente a alteração no container vinculado.
- Também cria um backup antes de aplicar a modificação.

![Salvar e Aplicar](/documentation/images/salva_e_aplicar.png)

### Aplicar

- Aplica o conteúdo editado no container sem salvar backup.
- Útil para alterações rápidas em testes, mas menos seguro.

![Aplicar](/documentation/images/aplicar.png)

### Reiniciar container

- Reinicia o container vinculado ao arquivo selecionado.
- Pode ser usado após grandes mudanças de configuração.

![Reiniciar container](/documentation/images/reiniciar_container.png)

### Validar

- Executa uma validação sintática e estrutural do arquivo de configuração.
- Suporta YAML (.yaml, .yml) e XML (.xml).
- Em caso de erro, mostra linha/coluna e a mensagem do problema; nenhuma alteração é aplicada ao arquivo.

![Validar](/documentation/images/validar.png)

### Diferenças

- Mostra um comparativo (diff) entre o conteúdo atual no editor e o que está salvo no arquivo.
- Útil para revisar alterações antes de aplicar.
- Se `DIFF_ALLOW_EDIT=true`, também é possível editar diretamente no modo diff.

![Diferenças](/documentation/images/diferencas.png)

![Editor Diff](/documentation/images/editor_diff.png)

### Voltar ao Editor

- Botão exibido apenas quando o modo Diferenças (diff) está ativo.
- Enquanto o diff está aberto, os demais botões da barra de ações (Salvar & Aplicar, Aplicar, Reiniciar container, Validar, Versões, Excluir) ficam desabilitados.
- Serve para retornar ao editor normal, onde todas as ações voltam a ficar disponíveis.
- O conteúdo no editor permanece exatamente como estava antes de abrir o diff.

![Voltar ao Editor](/documentation/images/voltar_editor.png)

### Versões

- Lista as versões de backup do arquivo.
- Ao selecionar uma versão, ela é carregada no editor.
- Para gravar no arquivo atual, é necessário clicar em Salvar & Aplicar ou Aplicar.

![Versões](/documentation/images/versoes.png)

![Lista de versões](/documentation/images/menu_versoes.png)

### Excluir

- Permite excluir uma versão de backup previamente criada.
- ⚠️ É necessário selecionar um backup na lista de versões para poder excluir.
- ❌ Não é possível excluir o arquivo em uso.
- Se quiser remover completamente um arquivo do Config Editor, é preciso alterar o docker-compose.yml (variável `FILE_CONTAINERS`).

![Excluir](/documentation/images/excluir.png)

# Tutoriais relacionados

LINK1
LINK2
