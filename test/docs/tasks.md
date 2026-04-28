# Backlog de Tarefas

## Produtos

### 1. RF-01: Criação de Produtos
- **Requisitos Relacionados:** RF-01
- **Descrição Detalhada:** Esta tarefa requer a criação de produtos contendo nome, descrição e valores unitários (valores monetários). O sistema deve permitir a entrada de dados e armazenamento de dados em uma coleção. Os requisitos adicionais incluem o registro do fornecedor da unidade e cadastro do produtor.
- **Assunto:** Produtos

### 2. RF-02: Criação de Fornecedores
- **Requisitos Relacionados:** RF-01
- **Descrição Detalhada:** Esta tarefa requer o cadastro de fornecedores vinculados aos produtos. O sistema deve permitir a criação de novos fornecedores e associá-los aos produtos, incluindo CNPJ e contato.
- **Assunto:** Produtos

## Fornecedores

### 3. RF-03: Sistema para monitorar estoques
- **Requisitos Relacionados:** RF-01
- **Descrição Detalhada:** O sistema deve permitir a entrada de mercadorias, atualização da quantidade disponível e registro do preço de custo.
- **Assunto:** Fornecedores

### 4. RF-04: Sistema para exibir estoques
- **Requisitos Relacionados:** RF-01
- **Descrição Detalhada:** O sistema deve permitir a saída de mercadorias e decrementar o saldo atual do estoque.
- **Assunto:** Fornecedores

## Notificação de QNTM (Quantidade Necessária para Segurança)

### 5. RF-05: Emissão de Notificação Visual ou por E-mail
- **Requisitos Relacionados:** RF-01, RF-06
- **Descrição Detalhada:** O sistema deve emitir uma notificação visual ou por e-mail quando um item atingir a quantidade mínima de segurança definida.
- **Assunto:** Notificação de QNTM (Quantidade Necessária para Segurança)

### 6. RF-06: Emissão de Notificação Visual ou por E-mail
- **Requisitos Relacionados:** RF-01, RF-06
- **Descrição Detalhada:** O sistema deve emitir uma notificação visual ou por e-mail quando um item atingir a quantidade mínima de segurança definida.
- **Assunto:** Notificação de QNTM (Quantidade Necessária para Segurança)

## Relatório

### 7. Tarefa 01
- **Requisitos Relacionados:** Nenhum
- **Descrição Detalhada:** Este é o relatório de desenvolvimento que será elaborado.
- **Assunto:** Relatório

## Cadastro de Produtos

### 8. RF-01 - Cadastro de Produtos
- **Requisitos Relacionados:** RF-02, RF-03
- **Descrição Detalhada:** O sistema deve permitir o registro e cadastro de produtos através do campo nome, descrição e código de barras (EAN). Os fornecedores devem ser informados nessa célula.
- **Assunto:** Cadastro de Produtos

## Gestão de Fornecedores

### 9. RF-02 - Gestão de Fornecedores
- **Requisitos Relacionados:** RF-01
- **Descrição Detalhada:** O sistema deve permitir a cadastro e registro de fornecedores, incluindo CNPJ, razão social e contato. Os produtos devem ser associados à esses dados.
- **Assunto:** Gestão de Fornecedores

## Entrada de Mercadoria

### 10. RF-03 - Entrada de Mercadoria
- **Requisitos Relacionados:** RF-01
- **Descrição Detalhada:** O sistema deve permitir o registro e entrada de mercadorias no campo estoque, incluindo nome, descrição, unidade de medida e categoria.
- **Assunto:** Entrada de Mercadoria

## Saída de Mercadoria

### 11. RF-04 - Saída de Mercadoria
- **Requisitos Relacionados:** RF-01, RF-02
- **Descrição Detalhada:** O sistema deve permitir o registro e saída de mercadorias do estoque, incluindo nome, descrição, unidade de medida e valor.
- **Assunto:** Saída de Mercadoria

## Alerta de Estoque Mínimo

### 12. RF-05 - Alerta de Estoque Mínimo
- **Requisitos Relacionados:** RF-01, RF-02, RF-03
- **Descrição Detalhada:** O sistema deve emitir uma notificação visual ou por e-mail quando o estoque atingir a quantidade mínima definida.
- **Assunto:** Alerta de Estoque Mínimo

## Histórico de Movimentações

### 13. RF-06 - Histórico de Movimentações
- **Requisitos Relacionados:** RF-01, RF-02
- **Descrição Detalhada:** O sistema deve gerar um histórico de movimentações, incluindo data, hora e usuário responsável.
- **Assunto:** Histórico de Movimentações

## Valorização de Estoque

### 14. RF-07 - Valorização de Estoque
- **Requisitos Relacionados:** RF-01, RF-02
- **Descrição Detalhada:** O sistema deve calcular o valor total do estoque utilizando métodos como PEPS (Primeiro que Entra, Primeiro que Sai) ou Custo Médio Ponderado.
- **Assunto:** Valorização de Estoque

## Relatório de Inventário

### 15. RF-08 - Relatório de Inventário
- **Requisitos Relacionados:** RF-01, RF-03
- **Descrição Detalhada:** O sistema deve gerar um relatório em PDF ou Excel listando todos os itens em estoque e seu status atual.
- **Assunto:** Relatório de Inventário

## Controle de Lotes e Validade

### 16. RF-09 - Controle de Lotes e Validade
- **Requisitos Relacionados:** RF-01, RF-02, RF-03
- **Descrição Detalhada:** O sistema deve permitir a gerenciamento de lote e validade, incluindo criação de lote e validação das mercadorias.
- **Assunto:** Controle de Lotes e Validade

## Gestão de Usuários e Perfis

### 17. RF-10 - Gestão de Usuários e Perfis
- **Requisitos Relacionados:** RF-01, RF-02
- **Descrição Detalhada:** O sistema deve permitir a criação de usuários, incluindo diferentes níveis de acesso (administrador, operador, almoxarife).
- **Assunto:** Gestão de Usuários e Perfis

## Importação de XML de NF-e

### 18. RF-11 - Importação de XML de NF-e
- **Requisitos Relacionados:** RF-01
- **Descrição Detalhada:** O sistema deve permitir a entrada de produtos via arquivo XML da Nota Fiscal Eletrônica (NF-e).
- **Assunto:** Importação de XML de NF-e

## Devolução de Itens

### 19. RF-12 - Devolução de Itens
- **Requisitos Relacionados:** RF-01
- **Descrição Detalhada:** O sistema deve prever a funcionalidade para o envio e recepção de itens devolvidos ao fornecedor ou pelo cliente.
- **Assunto:** Devolução de Itens

