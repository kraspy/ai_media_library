from django.conf import settings
from django.core.cache import cache
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI

from apps.core.models import ProjectSettings


def get_llm(temperature: float = 0.0):
    """
    Returns a configured LLM instance based on ProjectSettings.
    """
    cache.delete('project_settings')
    project_settings = ProjectSettings.load()
    provider = project_settings.llm_provider

    if provider == ProjectSettings.LLMProvider.DEEPSEEK:
        key = settings.DEEPSEEK_API_KEY
        return ChatDeepSeek(
            api_key=key,
            model=settings.DEEPSEEK_MODEL,
            temperature=temperature,
            api_base='https://api.deepseek.com',
        )
    else:
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=temperature,
        )
