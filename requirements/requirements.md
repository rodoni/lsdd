
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

## Requisitos Não Funcionais (RNF)
Estes definem as qualidades técnicas, restrições e critérios de operação do software.

13. **RNF01 - Desempenho:** O sistema deve processar consultas de saldo de estoque em menos de 2 segundos, mesmo com uma base de 10.000 itens.
14. **RNF02 - Disponibilidade:** O software deve estar disponível para operação 99% do tempo durante o horário comercial.
15. **RNF03 - Segurança (Autenticação):** O acesso ao sistema deve ser protegido por login e senha criptografada (ex: utilizando hashing como BCrypt).
16. **RNF04 - Portabilidade:** Por ser para fins didáticos, o sistema deve ser multiplataforma, operando em navegadores modernos (Chrome, Firefox, Edge).
17. **RNF05 - Backup:** O sistema deve realizar backup automático do banco de dados a cada 24 horas.
18. **RNF06 - Usabilidade:** O sistema deve possuir uma interface responsiva, permitindo que o almoxarife realize consultas rápidas via tablet ou smartphone.
19. **RNF07 - Integridade de Dados:** O sistema deve garantir que uma movimentação de estoque não seja processada se houver falha na conexão com o banco de dados (atomicidade).
20. **RNF08 - Documentação Técnica:** O sistema deve ser desenvolvido seguindo padrões de codificação claros e possuir documentação de API (ex: Swagger/OpenAPI) para futuras integrações.

---

