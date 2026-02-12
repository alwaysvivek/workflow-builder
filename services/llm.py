from groq import Groq
from core.config import settings
from core.prompts import PROMPTS
import json

class LLMService:
    def __init__(self):
        self.default_client = None
        if settings.GROQ_API_KEY:
            self.default_client = Groq(api_key=settings.GROQ_API_KEY)

    def get_client(self, api_key: str = None):
        if api_key:
            return Groq(api_key=api_key)
        return self.default_client

    async def run_step_stream(self, client: Groq, action: str, input_text: str, step_index: int):
        prompt_template = PROMPTS.get(action)
        if not prompt_template:
            yield json.dumps({"step": step_index + 1, "error": f"No prompt for {action}"}) + "\n"
            return

        full_prompt = prompt_template.format(input_text=input_text)

        try:
            stream = client.chat.completions.create(
                messages=[{"role": "user", "content": full_prompt}],
                model="llama-3.3-70b-versatile",
                stream=True
            )

            full_output = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_output += content
                    yield json.dumps({"step": step_index + 1, "chunk": content}) + "\n"
            
            # return full_output

        except Exception as e:
            yield json.dumps({"step": step_index + 1, "error": str(e)}) + "\n"
            raise e

llm_service = LLMService()
