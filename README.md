# Light Spec Driven Development (LSDD)

O **LSDD** é uma abordagem pragmática e automatizada para arquitetura de software assistida por IA. O objetivo dessa ferramenta de CLI é transformar documentações descentralizadas e textos brutos em especificações técnicas sólidas, diagramas arquiteturais em código e um backlog de engenharia estruturado.

A CLI se integra nativamente ao **OpenWebUI** para gerenciamento de "Knowledge Bases" através de RAG (Retrieval-Augmented Generation), e ao **vLLM** via `LangChain` para a inferência e orquestração de prompts de especialidade técnica de software.

---

## 🏗 Arquitetura do Projeto

Abaixo a estrutura principal desenhada no LSDD:

```text
lsdd/
├── main.py           # Entrypoint da CLI (via biblioteca Click)
├── core/
│   ├── api_client.py # Wrapper HTTP em requests para abstração do OpenWebUI
│   ├── chains.py     # Definição e execução lógica dos prompts utilizando LangChain
│   └── utils.py      # Funções utilitárias e file parsers
├── requirements.txt  # Dependências de execução (langchain, click, etc)
└── .env              # Variáveis e configurações de backend de inferência
```

---

## ⚙️ O Ciclo LSDD

A aplicação é dividida em **quatro comandos** principais que englobam a vida útil do planejamento técnico:

1. **`base` (Ingestão):** Automatiza coleções de conhecimento iterando sobre diretórios de arquivos Markdown (`.md`) e fazendo upload via chamadas de API para o OpenWebUI.
2. **`spec` (Definição de Produto):** Usa a base de conhecimento de referência para unificar em um único documento (`spec.md`) as funcionalidades, Requisitos Não-Funcionais (NFRs) e Regras de Negócio de alto nível.
3. **`plan` (O Core Técnico):** Inicia cadeias no vLLM para converter linguagem natural em modelagem técnica restrita. Gera diagramas em padrão [Mermaid.js](https://mermaid.js.org/) divididos em:
   - **Data Flow:** `sequenceDiagram` para o fluxo crítico.
   - **Domínio/Modelos:** `classDiagram` para as correlações estáticas de código.
   - **Infraestrutura/C4:** O gráfico de integração entre containers e banco de dados.
4. **`tasks` (Implementação Real):** Quebra todo o conhecimento (A Specs + O Design de Arquitetura Visual) para definir um **checklist acionável de backlogs práticos de desenvolvimento**.

---

## 🚀 Instalação e Configuração

Certifique-se de ter Python `3.10+` instalado.

```bash
# 1. Crie o isolamento em virtual environment
python -m venv venv
source venv/bin/activate

# 2. Instale as engines e requests listados no projeto
pip install -r requirements.txt

# 3. Configure as variáveis
cp .env.example .env
```

**Parâmetros de Ambiente (`.env`):**
Você deverá obrigatoriamente preencher onde seus serviços residem localmente:
```ini
OPENWEBUI_BASE_URL="http://localhost:3000"
OPENWEBUI_API_KEY="sk-...."

VLLM_BASE_URL="http://localhost:8000/v1"
VLLM_API_KEY="none"
VLLM_MODEL="llama3-8b-instruct"
```

---

## 📖 Instruções de Uso

As execuções operam numa topologia linear, onde o passo 1 produz o ID fundamental (`knowledge_id`). O UUID referenciado é a ponte semântica em todos os processos de "Reasoning".

### 1. Ingestão Automática

Passe sempre um diretório-raiz de documentação de regras de negócio originais. 
*(Ao final, a CLI te retorna um ID para ser anotado)*
```bash
python main.py base ~/meus_documentos/ "Zephyr Alpha Knowledge"
```

### 2. Geração da Especificação

Sintetiza as milhares de palavras do contexto numa Spec rígida.
```bash
python main.py spec <ID_DA_BASE> --output docs/spec.md
```

### 3. Geração do Design Arquitetural

Gera o arquivo com base de renderização de arquitetura e infraestrutura (Sendo compatível com renderizadores live de Markdowns modernos).
```bash
python main.py plan <ID_DA_BASE> --output docs/plan.md
```

### 4. Eng Checklist / Backlog

Une a bagagem anterior e infere as "User Stories" / Tarefas técnicas primárias num layout em caixas de listagem:
```bash
python main.py tasks <ID_DA_BASE> --plan-file docs/plan.md --output docs/tasks.md
```
