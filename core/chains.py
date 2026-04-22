import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .api_client import OpenWebUIClient

def fetch_explicit_context(knowledge_id: str) -> str:
    """Busca o texto completo de todos os documentos da base para contornar a fragmentação do RAG vetorial."""
    base_url = os.getenv("OPENWEBUI_BASE_URL", "http://localhost:3000")
    api_key = os.getenv("OPENWEBUI_API_KEY", "")
    if not api_key:
        return "Nenhum contexto encontrado (API Key não configurada)."
    
    try:
        client = OpenWebUIClient(base_url, api_key)
        content = client.get_knowledge_content(knowledge_id)
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

    return ChatOpenAI(
        base_url=base_url,
        api_key=api_key,
        model=model,
        temperature=0.2
    )

def generate_specification(knowledge_id: str, model_name: str = None) -> str:
    """
    Usa o LLM para ler o conteúdo da base e gerar o documento de especificação (spec.md).
    A sintaxe "#{knowledge_id}" assume que se estivermos passando isso para o proxy do OpenWebUI,
    ele fará o RAG debaixo dos panos. 
    Se não for usar o proxy do OpenWebUI, você precisará injetar o texto manualmente.
    """
    llm = get_llm()
    if model_name:
        llm.model_name = model_name

    context = fetch_explicit_context(knowledge_id)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software Especialista. Seu objetivo é analisar os requisitos e "
                   "unificar a visão do projeto em um documento de Especificação Técnica.\n"
                   "O documento DEVE conter as seguintes seções:\n"
                   "1. Um overview arquitetural\n"
                   "2. Funcionalidades Principais\n"
                   "3. Requisitos Não-funcionais\n"
                   "4. Regras de Negócio chave.\n"
                   "Responda apenas com o conteúdo em Markdown puro, sem introduções extras."),
        ("human", "Baseado exclusivamente nos documentos abaixo, gere o documento spec.md associado.\n\n"
                  "--- DOCUMENTAÇÃO DE REFERÊNCIA ---\n"
                  "{context}\n\n"
                  "Gere o spec.md:")
    ])

    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({"context": context})

def generate_architecture_plan(knowledge_id: str, model_name: str = None) -> str:
    """
    Executa múltiplos prompts especializados para gerar diagramas Mermaid 
    baseados no knowledge de referência da especificação.
    """
    import logging
    llm = get_llm()
    if model_name:
        llm.model_name = model_name
    context = fetch_explicit_context(knowledge_id)
        
    print("[1/3] Gerando diagrama de fluxo de dados (Sequência)...")
    seq_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Gere APENAS um bloco de código Markdown com um diagrama Mermaid.js do tipo 'sequenceDiagram' que descreva o fluxo de dados principal do sistema. Sem explicações adicionais."),
        ("human", "Com base na documentação abaixo, gere o diagrama de Sequência.\n\n{context}")
    ])
    
    print("[2/3] Gerando diagrama de classes/entidades (Class)...")
    class_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Gere APENAS um bloco de código Markdown com um diagrama Mermaid.js do tipo 'classDiagram' detalhando a estrutura de entidades, classes e relações. Sem explicações adicionais."),
        ("human", "Com base na documentação abaixo, gere o diagrama de Classes.\n\n{context}")
    ])
    
    print("[3/3] Gerando diagrama de infraestrutura (Componentes)...")
    comp_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Gere APENAS um bloco de código Markdown com um diagrama Mermaid.js (graph TD ou C4) evidenciando os componentes do sistema, infraestrutura e integrações. Sem explicações adicionais."),
        ("human", "Com base na documentação abaixo, gere o diagrama de Componentes.\n\n{context}")
    ])
    
    seq_chain = seq_prompt | llm | StrOutputParser()
    class_chain = class_prompt | llm | StrOutputParser()
    comp_chain = comp_prompt | llm | StrOutputParser()
    
    seq_result = seq_chain.invoke({"context": context})
    class_result = class_chain.invoke({"context": context})
    comp_result = comp_chain.invoke({"context": context})
    
    plan_md = (
        "# Plano de Arquitetura\n\n"
        "## 1. Fluxo de Dados Principal (Sequência)\n\n"
        f"{seq_result}\n\n"
        "## 2. Estrutura de Domínio / Classes\n\n"
        f"{class_result}\n\n"
        "## 3. Integração de Componentes e Infraestrutura\n\n"
        f"{comp_result}\n"
    )
    
    return plan_md

def generate_tasks_backlog(knowledge_id: str, plan_content: str = None, model_name: str = None) -> str:
    """
    Usa o LLM para ler o conteúdo da base e (opcionalmente) o plano arquitetural,
    gerando um backlog de tarefas em formato Markdown (checklist de engenharia).
    """
    llm = get_llm()
    if model_name:
        llm.model_name = model_name
    context = fetch_explicit_context(knowledge_id)
        
    system_prompt = (
        "Você é um Tech Lead e Engenheiro Sênior. Sua tarefa é quebrar a especificação e arquitetura "
        "do sistema em um backlog de tarefas práticas de engenharia de software.\n"
        "Gere a saída em formato de lista de Checklist Markdown (ex: - [ ] Configurar boilerplate de testes).\n"
        "Estruture as tarefas por domínios, épicos ou camadas lógicas (ex: Infraestrutura, Backend, Frontend, CI/CD)."
    )
    
    if plan_content:
        human_prompt = (
            "Com base na documentação a seguir e no planejamento arquitetural:\n\n"
            "--- DOCUMENTAÇÃO DE REFERÊNCIA ---\n"
            f"{context}\n\n"
            "--- PLANO ARQUITETURAL ---\n"
            f"```\n{plan_content}\n```\n\n"
            "Gere o checklist de tarefas de engenharia detalhado."
        )
    else:
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
