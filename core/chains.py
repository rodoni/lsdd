import os
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .api_client import OpenWebUIClient

def fetch_explicit_context(knowledge_id: str, use_rag: bool = False, query: str = "") -> str:
    """Busca o texto completo ou trechos via RAG para contornar a fragmentação/limite de contexto."""
    base_url = os.getenv("OPENWEBUI_BASE_URL", "http://localhost:3000")
    api_key = os.getenv("OPENWEBUI_API_KEY", "")
    if not api_key:
        return "Nenhum contexto encontrado (API Key não configurada)."
    
    try:
        client = OpenWebUIClient(base_url, api_key)
        content = client.get_knowledge_content(knowledge_id, use_rag=use_rag, query=query)
        return content if content else "A base de conhecimento parece estar vazia ou os arquivos ainda não foram processados."
    except Exception as e:
        return f"Erro ao buscar contexto da base: {e}"

def get_llm():
    """
    Retorna a instância do modelo configurada.
    Por padrão apontamos para o vLLM (para geração rápida),
    mas se estivermos usando RAG interno do OpenWebUI via tags ("#knowledge_id"),
    pode ser necessário apontar o base_url para o proxy do OpenWebUI.
    """
    # A prioridade é usar o LLM através do próprio OpenWebUI para que as tags de Knowledge Base funcionem.
    # Caso você deseje bater direto no vLLM, troque as variáveis de ambiente.
    base_url = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
    api_key = os.getenv("VLLM_API_KEY", "none")
    model = os.getenv("VLLM_MODEL", "llama3-8b-instruct")
    client = httpx.Client(verify=False, timeout=60)
    
    return ChatOpenAI(
        base_url=base_url,
        api_key=api_key,
        model=model,
        temperature=0.2,
        http_client=client
    )

def generate_specification(knowledge_id: str, model_name: str = None, use_rag: bool = False) -> str:
    """
    Usa o LLM para ler o conteúdo da base e gerar o documento de especificação (spec.md).
    """
    llm = get_llm()
    if model_name:
        llm.model_name = model_name

    # Se estiver usando RAG, passamos uma query direcionada para a Spec
    query = "funcionalidades, requisitos funcionais, requisitos não funcionais, regras de negócio" if use_rag else ""
    context = fetch_explicit_context(knowledge_id, use_rag=use_rag, query=query)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Seu trabalho é LER os requisitos fornecidos pelo usuário e SINTETIZAR um documento técnico. NÃO invente informações. Use APENAS o que foi fornecido."),
        ("human", "Abaixo estão os requisitos brutos do sistema:\n\n"
                  "```\n"
                  "{context}\n"
                  "```\n\n"
                  "Com base nos requisitos acima, crie um documento Markdown (`spec.md`) contendo exatamente estas 3 seções:\n"
                  "1. **Overview Arquitetural**: Um resumo do que é o sistema.\n"
                  "2. **Funcionalidades Principais**: Liste o que o sistema faz.\n"
                  "3. **Regras de Negócio chave**: Liste as regras importantes.\n\n"
                  "Escreva o conteúdo de forma detalhada e profissional. Responda apenas com o Markdown.")
    ])

    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({"context": context})

def generate_architecture_plan(knowledge_id: str, model_name: str = None, use_rag: bool = False) -> str:
    """
    Executa múltiplos prompts especializados para gerar diagramas Mermaid 
    baseados no knowledge de referência da especificação.
    """
    import logging
    llm = get_llm()
    if model_name:
        llm.model_name = model_name

    query = "arquitetura, diagrama de sequencia, componentes, infraestrutura, fluxo de dados, diagramas UML" if use_rag else ""
    context = fetch_explicit_context(knowledge_id, use_rag=use_rag, query=query)
        
    print("[1/5] Gerando diagrama de fluxo de dados (Sequência)...")
    seq_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Gere APENAS um bloco de código Markdown com um diagrama Mermaid.js do tipo 'sequenceDiagram' que descreva o fluxo de dados principal do sistema. Sem explicações adicionais."),
        ("human", "Com base na documentação abaixo, gere o diagrama de Sequência.\n\n{context}")
    ])
    
    print("[2/5] Gerando diagrama de classes/entidades (Class)...")
    class_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Gere APENAS um bloco de código Markdown com um diagrama Mermaid.js do tipo 'classDiagram' detalhando a estrutura de entidades, classes e relações. Sem explicações adicionais."),
        ("human", "Com base na documentação abaixo, gere o diagrama de Classes.\n\n{context}")
    ])
    
    print("[3/5] Gerando diagrama de Casos de Uso (Use Case)...")
    usecase_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Gere APENAS um bloco de código Markdown com um diagrama Mermaid.js (use 'flowchart TD' ou 'graph TD') que represente um Diagrama de Casos de Uso, evidenciando as interações entre os atores (usuários/sistemas) e as funcionalidades principais do sistema. Sem explicações adicionais."),
        ("human", "Com base na documentação abaixo, gere o diagrama de Casos de Uso.\n\n{context}")
    ])

    print("[4/5] Gerando diagrama de Atividades (Activity)...")
    activity_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Gere APENAS um bloco de código Markdown com um diagrama Mermaid.js (use 'flowchart TD' ou 'stateDiagram-v2') que represente um Diagrama de Atividades, descrevendo o fluxo passo a passo de um processo de negócio principal do sistema, incluindo decisões e ações. Sem explicações adicionais."),
        ("human", "Com base na documentação abaixo, gere o diagrama de Atividades.\n\n{context}")
    ])

    print("[5/5] Gerando diagrama de Estados (State)...")
    state_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Gere APENAS um bloco de código Markdown com um diagrama Mermaid.js do tipo 'stateDiagram-v2' que represente um Diagrama de Estados, focando no ciclo de vida da entidade mais importante do sistema (ex: Status de Pedido, Status de Usuário). Sem explicações adicionais."),
        ("human", "Com base na documentação abaixo, gere o diagrama de Estados.\n\n{context}")
    ])
    
    seq_chain = seq_prompt | llm | StrOutputParser()
    class_chain = class_prompt | llm | StrOutputParser()
    usecase_chain = usecase_prompt | llm | StrOutputParser()
    activity_chain = activity_prompt | llm | StrOutputParser()
    state_chain = state_prompt | llm | StrOutputParser()
    
    seq_result = seq_chain.invoke({"context": context})
    class_result = class_chain.invoke({"context": context})
    usecase_result = usecase_chain.invoke({"context": context})
    activity_result = activity_chain.invoke({"context": context})
    state_result = state_chain.invoke({"context": context})
    
    plan_md = (
        "# Plano de Arquitetura\n\n"
        "## 1. Fluxo de Dados Principal (Sequência)\n\n"
        f"{seq_result}\n\n"
        "## 2. Estrutura de Domínio / Classes\n\n"
        f"{class_result}\n\n"
        "## 3. Atores e Funcionalidades (Casos de Uso)\n\n"
        f"{usecase_result}\n\n"
        "## 4. Fluxo de Negócios (Atividades)\n\n"
        f"{activity_result}\n\n"
        "## 5. Ciclo de Vida e Mudanças de Estado (Estados)\n\n"
        f"{state_result}\n"
    )
    
    return plan_md

def generate_tasks_backlog(knowledge_id: str, model_name: str = None, use_rag: bool = False) -> str:
    """
    Usa o LLM para ler o conteúdo da base,
    gerando um backlog de tarefas em formato Markdown (checklist de engenharia).
    """
    llm = get_llm()
    if model_name:
        llm.model_name = model_name

    query = "tarefas de desenvolvimento, épicos, backlog, implementação, infraestrutura, frontend, backend" if use_rag else ""
    context = fetch_explicit_context(knowledge_id, use_rag=use_rag, query=query)
        
    system_prompt = (
        "Você é um Tech Lead e Engenheiro Sênior. Sua tarefa é quebrar a especificação e arquitetura "
        "do sistema em um backlog de tarefas práticas de engenharia de software.\n"
        "Gere a saída em formato de lista de Checklist Markdown (ex: - [ ] Configurar boilerplate de testes).\n"
        "Estruture as tarefas por domínios, épicos ou camadas lógicas (ex: Infraestrutura, Backend, Frontend, CI/CD) e associe cada tarefa a um numero de requisito, se houver. "
        "Se não houver um requisito associado, deixe como N/A.\n"
        "Lembrando que um requisito pode estar associado a mais de uma tarefa.\n"
        "O formato de saída deve ser:"
        "- [ ] **Título da Tarefa** (Requisito: Req. 1)\n"
        "  - Descrição detalhada da tarefa.\n"
    )
    
    human_prompt = (
        "Com base na documentação a seguir:\n\n"
        "--- DOCUMENTAÇÃO DE REFERÊNCIA ---\n"
        f"{context}\n\n"
        "Gere o checklist de tarefas de engenharia detalhado."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({})
