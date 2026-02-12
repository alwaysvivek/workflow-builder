import os
from pathlib import Path
from dotenv import load_dotenv

# Calculate path to .env file (parent of core is root)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

class Settings:
    PROJECT_NAME: str = "Workflow Builder"
    VERSION: str = "2.0.0"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./workflow.db")
    
    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")

settings = Settings()
