from dotenv import load_dotenv
import os
from pathlib import Path

# Encontra o diretório raiz do projeto (onde está o .env)
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"

# Carrega as variáveis do .env
load_dotenv(dotenv_path=env_path)

OPENROUTER_API = os.getenv("OPENROUTER_API_KEY")
LITERAL_MODELS = [
    "llama-4-maverick",  # Modelo principal - melhor performance no teste
    "claude-4-sonnet",
    "google-gemini-2.5-pro",
]

# Configuração de Timeout Global (em segundos)
WORKFLOW_TIMEOUT_SECONDS = int(os.getenv("WORKFLOW_TIMEOUT_SECONDS", "120"))
PROMPT_LAAJ = "langchain-ai/pairwise-evaluation-2"