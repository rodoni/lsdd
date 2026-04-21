import os
from pathlib import Path

def find_markdown_files(directory: str) -> list[Path]:
    """Busca recursivamente por todos os arquivos .md em um diretório."""
    base_path = Path(directory)
    if not base_path.exists() or not base_path.is_dir():
        raise FileNotFoundError(f"Diretório não encontrado: {directory}")
    return list(base_path.rglob("*.md"))
