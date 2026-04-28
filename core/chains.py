import os
import httpx
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

    if use_rag:
        llm = llm.bind(extra_body={"files": [{"type": "collection", "id": knowledge_id}]})
        context = "O CONTEXTO SERÁ FORNECIDO PELO SISTEMA DE RAG (OPENWEBUI)."
    else:
        context = fetch_explicit_context(knowledge_id)

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

    if use_rag:
        llm = llm.bind(extra_body={"files": [{"type": "collection", "id": knowledge_id}]})
        context = "O CONTEXTO SERÁ FORNECIDO PELO SISTEMA DE RAG (OPENWEBUI)."
    else:
        context = fetch_explicit_context(knowledge_id)
        
    print("[1/3] Gerando diagrama de fluxo (Flowchart)...")
    flow_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Gere APENAS um bloco de código Markdown com um diagrama Mermaid.js do tipo 'flowchart TD' que descreva o fluxo geral ou macroarquitetura do sistema. Sem explicações adicionais."),
        ("human", "Com base na documentação abaixo, gere o diagrama de Fluxo.\n\n{context}")
    ])

    print("[2/3] Gerando diagrama de fluxo de dados (Sequência)...")
    seq_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Gere APENAS um bloco de código Markdown com um diagrama Mermaid.js do tipo 'sequenceDiagram' que descreva o fluxo de dados principal do sistema. Sem explicações adicionais."),
        ("human", "Com base na documentação abaixo, gere o diagrama de Sequência.\n\n{context}")
    ])
    
    print("[3/3] Gerando diagrama de classes/entidades (Class)...")
    class_prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um Arquiteto de Software. Gere APENAS um bloco de código Markdown com um diagrama Mermaid.js do tipo 'classDiagram' detalhando a estrutura de entidades, classes e relações. Sem explicações adicionais."),
        ("human", "Com base na documentação abaixo, gere o diagrama de Classes.\n\n{context}")
    ])
    
    flow_chain = flow_prompt | llm | StrOutputParser()
    seq_chain = seq_prompt | llm | StrOutputParser()
    class_chain = class_prompt | llm | StrOutputParser()
    
    flow_result = flow_chain.invoke({"context": context})
    seq_result = seq_chain.invoke({"context": context})
    class_result = class_chain.invoke({"context": context})
    
    plan_md = (
        "# Plano de Arquitetura\n\n"
        "## 1. Fluxo Geral (Macroarquitetura)\n\n"
        f"{flow_result}\n\n"
        "## 2. Fluxo de Dados Principal (Sequência)\n\n"
        f"{seq_result}\n\n"
        "## 3. Estrutura de Domínio / Classes\n\n"
        f"{class_result}\n"
    )
    
    return plan_md

def generate_tasks_backlog(knowledge_id: str, model_name: str = None, use_rag: bool = False) -> str:
    """
    Usa o LLM para ler o conteúdo da base,
    gerando um backlog de tarefas em formato Markdown (checklist de engenharia).
    Verifica também se todos os requisitos foram cobertos, e se não, 
    faz prompts adicionais explicitamente para cada requisito faltante.
    """
    llm = get_llm()
    if model_name:
        llm.model_name = model_name

    if use_rag:
        llm = llm.bind(extra_body={"files": [{"type": "collection", "id": knowledge_id}]})
        context = "O CONTEXTO SERÁ FORNECIDO PELO SISTEMA DE RAG (OPENWEBUI)."
    else:
        context = fetch_explicit_context(knowledge_id)
        
    system_prompt = (
        "Você é um Tech Lead e Engenheiro Sênior. Sua tarefa é quebrar a especificação "
        "do sistema em um backlog de tarefas práticas de engenharia de software.\n"
        "Gere a saída em formato de lista de Checklist Markdown (ex: - [ ] Configurar boilerplate de testes).\n"
        "Estruture as tarefas por assuntos.\n\n"
        "REGRAS OBRIGATÓRIAS:\n"
        "1. TODOS os requisitos detalhados na documentação DEVEM obrigatoriamente ser cobertos por pelo menos uma task no backlog.\n"
        "2. O formato de saída deve seguir os modelos abaixo:\n\n"
        "- [ ] **Título da Tarefa** (Requisito: Req. 1)\n"
        "  - Descrição detalhada da tarefa.\n\n"
    )
    
    human_prompt = (
        "Com base na documentação a seguir:\n\n"
        "--- DOCUMENTAÇÃO DE REFERÊNCIA ---\n"
        "{context}\n\n"
        "Gere o checklist de tarefas de engenharia detalhado."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm | StrOutputParser()
    initial_output = chain.invoke({"context": context})
    
    # --- Nova Lógica de Verificação de Requisitos Faltantes ---
    verify_system_prompt = (
        "Você é um auditor de requisitos. "
        "Você deve verificar se TODOS os requisitos listados na sua base de conhecimento (documentação) "
        "foram contemplados no checklist gerado.\n"
        "Retorne APENAS uma lista separada por vírgula com os números ou identificadores dos requisitos "
        "(ex: Req. 1, Req. 2, RF-03) que estão presentes na documentação mas NÃO foram citados no checklist.\n"
        "Se todos os requisitos da documentação foram contemplados no checklist, ou se não houver requisitos explícitos na documentação, "
        "responda EXATAMENTE a palavra: NENHUM."
    )
    
    verify_human_prompt = (
        "Aqui está o checklist gerado:\n\n{checklist}\n\n"
        "A documentação de referência é:\n{context}\n\n"
        "Quais requisitos da documentação NÃO foram citados no checklist? Retorne apenas a lista separada por vírgula ou NENHUM."
    )
    
    verify_prompt_template = ChatPromptTemplate.from_messages([
        ("system", verify_system_prompt),
        ("human", verify_human_prompt)
    ])
    
    verify_chain = verify_prompt_template | llm | StrOutputParser()
    missing_reqs_response = verify_chain.invoke({
        "checklist": initial_output,
        "context": context
    })
    
    missing_reqs_str = missing_reqs_response.strip()
    
    # Se encontrou requisitos não citados
    if missing_reqs_str.upper() != "NENHUM" and missing_reqs_str:
        # Extrai a lista de requisitos faltantes
        missing_reqs = [r.strip() for r in missing_reqs_str.split(",") if r.strip()]
        
        adicionais_output = ""
        for req in missing_reqs:
            # Pula textos longos que possam ser alucinação do modelo
            if len(req) > 50:
                continue
                
            req_system_prompt = system_prompt
            req_human_prompt = (
                "O requisito '{req}' presente na documentação não foi contemplado anteriormente no checklist.\n"
                "A documentação de referência é:\n{context}\n\n"
                "Gere as tarefas de engenharia APENAS para cobrir o requisito '{req}', "
                "seguindo rigorosamente as mesmas regras e formato de checklist definido no system prompt."
            )
            
            req_prompt_template = ChatPromptTemplate.from_messages([
                ("system", req_system_prompt),
                ("human", req_human_prompt)
            ])
            
            req_chain = req_prompt_template | llm | StrOutputParser()
            req_output = req_chain.invoke({
                "req": req,
                "context": context
            })
            
            adicionais_output += f"\n\n### Tarefas Adicionais para {req}\n\n{req_output}"
            
        return initial_output + adicionais_output

    return initial_output
