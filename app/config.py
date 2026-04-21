import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./lxp.db")
SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
SESSION_COOKIE_NAME: str = os.getenv("SESSION_COOKIE_NAME", "lxp_session")
AZURE_EVENTS_CACHE_TTL_HOURS: int = int(os.getenv("AZURE_EVENTS_CACHE_TTL_HOURS", "6"))