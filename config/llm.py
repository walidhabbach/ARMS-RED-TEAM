"""Provider switch for Agno agents: OpenRouter or local Ollama."""
import os
from dotenv import load_dotenv

load_dotenv()


def get_model(provider: str | None = None):
    selected = (provider or os.getenv("LLM_PROVIDER", "openrouter")).strip().lower()

    if selected == "openrouter":
        from agno.models.openrouter import OpenRouter

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is missing. Add it to your .env file.")
        model_id = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        return OpenRouter(id=model_id, api_key=api_key)

    if selected == "ollama":
        from agno.models.ollama import Ollama

        model_id = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        return Ollama(id=model_id, host=host, api_key=None)

    raise ValueError("Unsupported LLM_PROVIDER. Choose 'openrouter' or 'ollama'.")
