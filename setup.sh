#!/bin/bash
set -e

echo "====================================="
echo "  Configurando ambiente LSDD...      "
echo "====================================="

# Verificar se o Python 3.10+ está disponível
if ! command -v python3 &> /dev/null
then
    echo "ERRO: python3 não encontrado."
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "-> Criando virtual environment (venv)..."
    python3 -m venv venv
else
    echo "-> Virtual environment já existe."
fi

# Ativar venv
echo "-> Ativando venv..."
source venv/bin/activate

# Instalar o projeto e as dependências
echo "-> Instalando o projeto em modo iterativo (editable) com suas dependências..."
pip install --upgrade pip
pip install -e .

# Configurar o arquivo .env se necessário
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "-> Criando arquivo .env a partir de .env.example..."
    cp .env.example .env
    echo "AVISO: Por favor, não esqueça de configurar as variáveis (como OPENWEBUI_API_KEY) no arquivo .env!"
fi

echo "====================================="
echo "Ambiente configurado com sucesso!"
echo "Para começar a usar, ative o ambiente virtual executando:"
echo ""
echo "    source venv/bin/activate"
echo ""
echo "Em seguida, você pode testar a CLI:"
echo ""
echo "    lsdd --help"
echo "====================================="
