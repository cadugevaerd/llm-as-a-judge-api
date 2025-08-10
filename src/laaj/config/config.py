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
    "claude-4-sonnet",
    "google-gemini-2.5-pro",
]