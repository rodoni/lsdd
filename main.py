import os
import click
from dotenv import load_dotenv
from core.api_client import OpenWebUIClient
from core.utils import find_markdown_files
from core.chains import generate_specification, generate_architecture_plan, generate_tasks_backlog

load_dotenv()

@click.group()
def cli():
    """LSDD - Light Spec Driven Development CLI"""
    pass

@cli.command("base")
@click.argument("directory", type=click.Path(exists=True))
@click.argument("name", type=str)
def lsdd_base(directory, name):
    """
    Ingesta arquivos Markdown de um diretório em uma Knowledge Base do OpenWebUI.
    
    DIRECTORY: Caminho para a pasta com arquivos .md
    NAME: Nome da Collection/Knowledge Base
    """
    click.echo(f"Iniciando LSDD Base (Ingestão)...")
    click.echo(f"Diretório alvo: {directory}")
    click.echo(f"Nome da Knowledge Base: {name}")

    base_url = os.getenv("OPENWEBUI_BASE_URL", "http://localhost:3000")
    api_key = os.getenv("OPENWEBUI_API_KEY")

    if not api_key:
        click.secho("ERRO: OPENWEBUI_API_KEY não configurada no .env", fg="red")
        return

    client = OpenWebUIClient(base_url, api_key)

    try:
        md_files = find_markdown_files(directory)
        if not md_files:
            click.echo("Nenhum arquivo Markdown (.md) encontrado no diretório especificado.")
            return
            
        click.echo(f"Encontrados {len(md_files)} arquivos Markdown. Criando base de conhecimento...")
        
        knowledge_id = client.create_knowledge_base(name=name, description="Base gerada automaticamente via LSDD CLI")
        click.secho(f"Knowledge Base criada com sucesso! ID: {knowledge_id}", fg="green")
        
        for index, file_path in enumerate(md_files, 1):
            click.echo(f"[{index}/{len(md_files)}] Enviando {file_path.name}...")
            client.upload_document_to_knowledge(knowledge_id, file_path)
            
        click.secho(f"\nIngestão concluída com sucesso!", fg="green")
        click.secho(f"ID da base de conhecimento: {knowledge_id}", fg="cyan", bold=True)
        click.echo("Armazene este ID para usar nas próximas etapas do fluxo.")
        
    except Exception as e:
        click.secho(f"Erro durante a operação: {str(e)}", fg="red")

@cli.command("spec")
@click.argument("knowledge_id", type=str)
@click.option("--output", "-o", default="spec.md", help="Caminho do arquivo de saída (ex: docs/spec.md)")
def lsdd_spec(knowledge_id, output):
    """
    Especificação: Gera um documento spec.md unificado utilizando a Knowledge Base.
    
    KNOWLEDGE_ID: O UUID da base gerada no passo 'base'.
    """
    click.echo(f"Iniciando LSDD Spec (Definição)...")
    click.echo(f"Knowledge ID alvo: {knowledge_id}")
    
    try:
        click.echo("Solicitando geração da especificação ao LLM. Isso pode levar alguns minutos...")
        spec_content = generate_specification(knowledge_id)
        
        with open(output, "w", encoding="utf-8") as f:
            f.write(spec_content)
            
        click.secho(f"\nSucesso! Especificação gerada e salva em: {output}", fg="green")
        
    except Exception as e:
        click.secho(f"Erro ao gerar especificação: {str(e)}", fg="red")

@cli.command("plan")
@click.argument("knowledge_id", type=str)
@click.option("--output", "-o", default="plan.md", help="Caminho do arquivo de saída (ex: docs/plan.md)")
def lsdd_plan(knowledge_id, output):
    """
    Arquitetura: Traduz a especificação em diagramas estruturais Mermaid.js.
    
    KNOWLEDGE_ID: O UUID da base gerada no passo 'base'.
    """
    click.echo(f"Iniciando LSDD Plan (Arquitetura)...")
    click.echo(f"Knowledge ID alvo: {knowledge_id}")
    
    try:
        click.echo("Processando múltiplos prompts de arquitetura. Aguarde...")
        plan_content = generate_architecture_plan(knowledge_id)
        
        with open(output, "w", encoding="utf-8") as f:
            f.write(plan_content)
            
        click.secho(f"\nSucesso! Plano arquitetural gerado e salvo em: {output}", fg="green")
        
    except Exception as e:
        click.secho(f"Erro ao gerar plano: {str(e)}", fg="red")

@cli.command("tasks")
@click.argument("knowledge_id", type=str)
@click.option("--plan-file", "-p", type=click.Path(exists=True), help="Caminho opcional para o arquivo plan.md para dar mais contexto ao LLM.")
@click.option("--output", "-o", default="tasks.md", help="Caminho do arquivo de saída (ex: docs/tasks.md)")
def lsdd_tasks(knowledge_id, plan_file, output):
    """
    Implementação: Quebra o plano e os requisitos em unidades de trabalho (Backlog).
    
    KNOWLEDGE_ID: O UUID da base gerada no passo 'base'.
    """
    click.echo(f"Iniciando LSDD Tasks (Implementação)...")
    click.echo(f"Knowledge ID alvo: {knowledge_id}")
    
    plan_content = None
    if plan_file:
        click.echo(f"Lendo contexto arquitetural de: {plan_file}")
        with open(plan_file, "r", encoding="utf-8") as f:
            plan_content = f.read()
    
    try:
        click.echo("Solicitando geração do Engineering Backlog. Aguarde...")
        tasks_content = generate_tasks_backlog(knowledge_id, plan_content)
        
        with open(output, "w", encoding="utf-8") as f:
            f.write(tasks_content)
            
        click.secho(f"\nSucesso! Checklist de tarefas gerado e salvo em: {output}", fg="green")
        
    except Exception as e:
        click.secho(f"Erro ao gerar tarefas: {str(e)}", fg="red")

if __name__ == "__main__":
    cli()
