import os
import re
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field
from typing import List
from .api_client import OpenWebUIClient

def _clean_llm_output(output) -> str:
    text = output.content if hasattr(output, 'content') else str(output)
    text = re.sub(r"<think\b[^>]*>.*?</think\s*>", "", text, flags=re.DOTALL)
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```", "", text)
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        text = match.group(0)
    return text.strip()

class RequirementRef(BaseModel):
    id: str = Field(description="Identificador do requisito (ex: RF-01, REQ-001)")
    resumo: str = Field(description="Resumo breve do requisito")

class SubjectMapping(BaseModel):
    assunto: str = Field(description="Nome do assunto/domínio técnico")
    requisito_ids: List[str] = Field(description="Lista de IDs dos requisitos pertencentes a este assunto")

class RequirementSubjectExtraction(BaseModel):
    requisitos: List[RequirementRef] = Field(description="Lista completa de todos os requisitos encontrados na documentação")
    assuntos: List[SubjectMapping] = Field(description="Lista de assuntos mapeados com seus requisitos")

class TaskFormat(BaseModel):
    titulo_da_task: str = Field(description="Título curto e claro da task")
    assunto: str = Field(description="Assunto/domínio ao qual esta task pertence")
    requisitos_relacionados: List[str] = Field(description="Lista de IDs dos requisitos relacionados a esta task")
    descricao_detalhada: str = Field(description="Descrição detalhada da atividade a ser realizada")

class TaskList(BaseModel):
    tasks: List[TaskFormat] = Field(description="Lista de tarefas do backlog")

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

def _resolve_context(knowledge_id: str, use_rag: bool, llm):
    if use_rag:
        llm = llm.bind(extra_body={"files": [{"type": "collection", "id": knowledge_id}]})
        return "O CONTEXTO SERÁ FORNECIDO PELO SISTEMA DE RAG (OPENWEBUI).", llm
    return fetch_explicit_context(knowledge_id), llm

def generate_tasks_backlog(knowledge_id: str, model_name: str = None, use_rag: bool = False) -> str:
    """
    Abordagem em 4 etapas:
    1. Identifica todos os requisitos e assuntos, relacionando-os.
    2. Cria tarefas por assunto.
    3. Verifica cobertura e cria tarefas para requisitos não cobertos.
    4. Renderiza o backlog agrupado por assunto.
    """
    llm = get_llm()
    if model_name:
        llm.model_name = model_name

    context, llm = _resolve_context(knowledge_id, use_rag, llm)

    try:
        # ---- ETAPA 1: Identificar requisitos, assuntos e suas relações ----
        print("[1/4] Identificando requisitos e assuntos...")
        extraction_parser = PydanticOutputParser(pydantic_object=RequirementSubjectExtraction)
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Você é um Arquiteto de Software. Leia a documentação e execute:\n"
             "1. Identifique TODOS os requisitos. Cada requisito deve ter um ID único (ex: RF-01, REQ-001).\n"
             "2. Identifique os assuntos/domínios técnicos abordados.\n"
             "3. Relacione cada assunto aos IDs dos requisitos que pertencem a ele.\n\n"
             "IMPORTANTE: Responda APENAS com JSON válido. NÃO inclua texto adicional, markdown ou explicações.\n\n"
             "Formato esperado:\n"
             '{{\n'
             '  "requisitos": [\n'
             '    {{ "id": "RF-01", "resumo": "Resumo do requisito" }}\n'
             '  ],\n'
             '  "assuntos": [\n'
             '    {{ "assunto": "Nome do Assunto", "requisito_ids": ["RF-01", "RF-02"] }}\n'
             '  ]\n'
             '}}\n\n'
             "{format_instructions}"),
            ("human",
             "--- DOCUMENTAÇÃO DE REFERÊNCIA ---\n{context}\n\n"
             "Identifique TODOS os requisitos, os assuntos e suas relações. Responda APENAS com o JSON.")
        ]).partial(format_instructions=extraction_parser.get_format_instructions())

        extraction_chain = extraction_prompt | llm | RunnableLambda(_clean_llm_output) | extraction_parser
        extraction: RequirementSubjectExtraction = extraction_chain.invoke({"context": context})

        all_req_ids = {r.id for r in extraction.requisitos}
        req_lookup = {r.id: r.resumo for r in extraction.requisitos}
        print(f"   {len(all_req_ids)} requisitos em {len(extraction.assuntos)} assuntos.")

        # ---- ETAPA 2: Gerar tarefas por assunto ----
        print("[2/4] Gerando tarefas por assunto...")
        task_parser = PydanticOutputParser(pydantic_object=TaskList)
        all_tasks: list[TaskFormat] = []

        for subj in extraction.assuntos:
            req_details = []
            for rid in subj.requisito_ids:
                req_details.append(f"- {rid}: {req_lookup.get(rid, 'Sem descrição')}")
            req_list = "\n".join(req_details)

            task_prompt = ChatPromptTemplate.from_messages([
                ("system",
                 "Você é um Tech Lead. Crie tarefas de engenharia práticas para implementar os requisitos "
                 "do assunto fornecido. Cada requisito DEVE ser coberto por pelo menos uma tarefa.\n\n"
                 "IMPORTANTE: Responda APENAS com JSON válido. NÃO inclua texto adicional, markdown ou explicações.\n\n"
                 "Formato esperado:\n"
                 '{{\n'
                 '  "tasks": [\n'
                 '    {{\n'
                 '      "titulo_da_task": "Título da task",\n'
                 '      "assunto": "{assunto}",\n'
                 '      "requisitos_relacionados": ["RF-01"],\n'
                 '      "descricao_detalhada": "Descrição detalhada da atividade"\n'
                 '    }}\n'
                 '  ]\n'
                 '}}\n\n'
                 "{format_instructions}"),
                ("human",
                 "Assunto: {assunto}\n\n"
                 "Requisitos:\n{requisitos}\n\n"
                 "Crie as tarefas de engenharia para este assunto. Responda APENAS com o JSON.")
            ]).partial(format_instructions=task_parser.get_format_instructions())

            task_chain = task_prompt | llm | RunnableLambda(_clean_llm_output) | task_parser
            result: TaskList = task_chain.invoke({"assunto": subj.assunto, "requisitos": req_list})
            all_tasks.extend(result.tasks)

        # ---- ETAPA 3: Verificar cobertura ----
        print("[3/4] Verificando cobertura de requisitos...")
        covered = set()
        for t in all_tasks:
            covered.update(t.requisitos_relacionados)

        uncovered = all_req_ids - covered
        if uncovered:
            print(f"   {len(uncovered)} requisitos não cobertos. Criando tarefas complementares...")
            unc_details = [f"- {rid}: {req_lookup.get(rid, '')}" for rid in sorted(uncovered)]
            unc_list = "\n".join(unc_details)
            coverage_prompt = ChatPromptTemplate.from_messages([
                ("system",
                 "Você é um Tech Lead. Os requisitos abaixo não foram cobertos por nenhuma tarefa. "
                 "Crie tarefas para cobri-los. O campo 'assunto' deve ser preenchido com o domínio mais adequado.\n\n"
                 "IMPORTANTE: Responda APENAS com JSON válido. NÃO inclua texto adicional, markdown ou explicações.\n\n"
                 "Formato esperado:\n"
                 '{{\n'
                 '  "tasks": [\n'
                 '    {{\n'
                 '      "titulo_da_task": "Título da task",\n'
                 '      "assunto": "Nome do assunto",\n'
                 '      "requisitos_relacionados": ["RF-01"],\n'
                 '      "descricao_detalhada": "Descrição detalhada da atividade"\n'
                 '    }}\n'
                 '  ]\n'
                        "{format_instructions}"),
                ("human",
                 "Requisitos não cobertos:\n{uncovered}\n\n"
                 "Contexto original:\n{context}\n\n"
                 "Crie tarefas para cobrir estes requisitos. Responda APENAS com o JSON.")
            ]).partial(format_instructions=task_parser.get_format_instructions())

            coverage_chain = coverage_prompt | llm | RunnableLambda(_clean_llm_output) | task_parser
            extra: TaskList = coverage_chain.invoke({"uncovered": unc_list, "context": context})
            all_tasks.extend(extra.tasks)

        # ---- ETAPA 4: Renderização final agrupada por assunto ----
        print("[4/4] Renderizando backlog...")
        from collections import OrderedDict
        grouped: dict[str, list[TaskFormat]] = OrderedDict()
        for task in all_tasks:
            grouped.setdefault(task.assunto, []).append(task)

        md_output = "# Backlog de Tarefas\n\n"
        task_num = 1
        for assunto, tasks in grouped.items():
            md_output += f"## {assunto}\n\n"
            for task in tasks:
                reqs = ", ".join(task.requisitos_relacionados) if task.requisitos_relacionados else "Nenhum"
                md_output += f"### {task_num}. {task.titulo_da_task}\n"
                md_output += f"- **Requisitos Relacionados:** {reqs}\n"
                md_output += f"- **Descrição Detalhada:** {task.descricao_detalhada}\n"
                md_output += f"- **Assunto:** {task.assunto}\n\n"
                task_num += 1

        return md_output
    except Exception as e:
        return f"Erro ao gerar o backlog estruturado: {str(e)}"
