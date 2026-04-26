```
# Sistema de Controle de Estoque

## Overview Arquitetural

O sistema de controle de estoque é uma ferramenta vital para a gestão eficiente dos produtos em estabelecimento. Ele permite um gerenciamento detalhado, otimizando o uso e a manutenção de mercadorias. O projeto aborda os principais aspectos do sistema:

## Funcionalidades Principais

### 1. Cadastro de Produtos
O sistema deve permitir ao usuário cadastrar novos produtos com seus dados básicos (nome, descrição, código de barras EAN e categoria).

### 2. Gestão de Fornecedores
Os fornecedores podem ser adquiridos e inseridos nos arquivos de entrada/escrita.

### 3. Entrada de Mercadoria
O sistema permite a entrada de produtos em estoque e atualiza o saldo.

### 4. Saída de Mercadoria
Se necessário, o saldo do estoque é reduzido para atender aos pedidos.

## Regras de Negócio chave

1. **Inclusão de Valores**: O sistema calcula o valor total dos produtos, incluindo taxas e impostos.
2. **Validação de Stock**: Os dados de inventário são rastreáveis e otimizados para ações como venda e recuperação.
3. **Controle de Estoque Mínimo (PEPS)**: O sistema verifica se o estoque está suficientemente livre para futuros movimentos.

## Acompanhamento e Gerenciamento

- **Histórico de Movimentações**: Permite a percurso do estoque, classificando movimentos, data e usuário.
- **Relatório de Inventário**: Gera relatórios em PDF ou Excel mostrando os produtos no estoque atual.

## Usuários e Configurações
- **Usuários e Perfil**:
  - Administrador: Gestão global dos produtos.
  - Operador: Atualização da situação do estoque, controle de entrada e saída.
  - Almoxarife: Manutenção e rastreabilidade de itens no estoque.

## Relações Com outros Arquiteturas

### Importação de XML
- O sistema para a entrada de produtos via arquivo de importação (XML) do Nota Fiscal Eletrônica.

### Devolução de Itens
- A função que permite o estorno de movimentações em caso de devolução de mercadorias ao fornecedor ou pelo cliente.