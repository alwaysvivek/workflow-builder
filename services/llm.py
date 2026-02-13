from groq import Groq
from core.config import settings


class LLMService:
    def __init__(self):
        self.default_client = None
        if settings.GROQ_API_KEY:
            self.default_client = Groq(api_key=settings.GROQ_API_KEY)

    def get_client(self, api_key: str = None):
        if api_key:
            return Groq(api_key=api_key)
        return self.default_client


llm_service = LLMService()

