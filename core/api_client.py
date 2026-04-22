import requests
from pathlib import Path

class OpenWebUIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }

    def create_knowledge_base(self, name: str, description: str = "") -> str:
        """
        Cria uma nova Knowledge Base e retorna o seu ID.
        """
        url = f"{self.base_url}/api/v1/knowledge/create"
        payload = {
            "name": name,
            "description": description
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        return data.get("id")

    def upload_document_to_knowledge(self, knowledge_id: str, file_path: Path) -> dict:
        """
        Faz o upload de um arquivo e o vincula à Knowledge Base.
        No OpenWebUI isso exige 2 passos: upload do arquivo genérico, e adição do file_id na base de conhecimento.
        """
        import time
        
        # Passo 1: Upload para o repo de arquivos do webui
        upload_url = f"{self.base_url}/api/v1/files/"
        with open(file_path, "rb") as f:
            files = {
                "file": (file_path.name, f, "text/markdown")
            }
            upload_headers = {"Authorization": self.headers["Authorization"]}
            response = requests.post(upload_url, files=files, headers=upload_headers)
            response.raise_for_status()
            
            upload_data = response.json()
            file_id = upload_data.get("id")
            
            if not file_id:
                raise Exception("Falha ao obter ID do arquivo durante upload.")
                
        # Um pequeno delay pra dar tempo do backend mastigar o markdown rapidinho
        time.sleep(1)

        # Passo 2: Adicionar a relação na knowledge base
        link_url = f"{self.base_url}/api/v1/knowledge/{knowledge_id}/file/add"
        link_payload = {"file_id": file_id}
        
        link_response = requests.post(link_url, json=link_payload, headers=self.headers)
        link_response.raise_for_status()
            
        return link_response.json()

    def get_knowledge_content(self, knowledge_id: str) -> str:
        """
        Recupera o conteúdo completo de todos os arquivos associados a uma Knowledge Base.
        Isso é preferível ao RAG vetorial (chunking) quando precisamos que o LLM analise a especificação inteira.
        """
        url = f"{self.base_url}/api/v1/files/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        files_data = response.json().get("items", []) if "items" in response.json() else response.json()
        if not isinstance(files_data, list):
            # Fallback para versões do OpenWebUI que retornam a lista direto
            files_data = [files_data] if isinstance(files_data, dict) else files_data

        content_parts = []
        for file_item in files_data:
            meta = file_item.get("meta", {})
            # Em OpenWebUI, arquivos atrelados a uma KB possuem o ID da KB no meta.collection_name
            if meta.get("collection_name") == knowledge_id or file_item.get("collection_name") == knowledge_id:
                data = file_item.get("data", {})
                content = data.get("content", "")
                if content:
                    content_parts.append(f"--- Documento: {meta.get('name', 'N/A')} ---\n{content}\n")
                    
        return "\n".join(content_parts)
