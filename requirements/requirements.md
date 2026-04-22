
---

## Requisitos Funcionais (RF)
Estes descrevem as funcionalidades diretas e as interações que o usuário terá com o sistema.

1.  **RF01 - Cadastro de Produtos:** O sistema deve permitir o registro de produtos contendo nome, descrição, código de barras (EAN), unidade de medida e categoria.
2.  **RF02 - Gestão de Fornecedores:** O sistema deve permitir o cadastro de fornecedores vinculados aos produtos, incluindo CNPJ, razão social e contato.
3.  **RF03 - Entrada de Mercadoria:** O sistema deve permitir o registro de entradas de estoque, atualizando a quantidade disponível e registrando o preço de custo.
4.  **RF04 - Saída de Mercadoria:** O sistema deve permitir o registro de saídas (vendas ou baixas), decrementando o saldo atual do estoque.
5.  **RF05 - Alerta de Estoque Mínimo:** O sistema deve emitir uma notificação visual ou por e-mail quando um item atingir a quantidade mínima de segurança definida.
6.  **RF06 - Histórico de Movimentações:** O sistema deve manter um log (rastreabilidade) de todas as entradas e saídas, identificando data, hora e usuário responsável.
7.  **RF07 - Valorização de Estoque:** O sistema deve calcular o valor total do estoque utilizando métodos como PEPS (Primeiro que Entra, Primeiro que Sai) ou Custo Médio Ponderado.
8.  **RF08 - Relatório de Inventário:** O sistema deve gerar relatórios em PDF ou Excel listando todos os itens em estoque e seu status atual.
9.  **RF09 - Controle de Lotes e Validade:** O sistema deve permitir o rastreio de produtos por número de lote e data de vencimento (essencial para alimentos ou medicamentos).
10. **RF10 - Gestão de Usuários e Perfis:** O sistema deve permitir a criação de usuários com diferentes níveis de acesso (ex: Administrador, Operador, Almoxarife).
11. **RF11 - Importação de XML de NF-e:** O sistema deve permitir a entrada de produtos via importação do arquivo XML da Nota Fiscal Eletrônica.
12. **RF12 - Devolução de Itens:** O sistema deve prever uma funcionalidade para estorno de movimentações em caso de devolução de mercadoria ao fornecedor ou pelo cliente.

---
