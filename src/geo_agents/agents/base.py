from langchain_openai import ChatOpenAI
from geo_agents.config import settings


def get_llm(temperature: float = 0.1) -> ChatOpenAI:
    """Get OpenAI-compatible LLM client."""
    return ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=temperature,
    )


def create_agent_llm(system_prompt: str, tools: list | None = None, temperature: float = 0.1):
    """Create an LLM with system prompt and optional tool binding."""
    llm = get_llm(temperature)
    if tools:
        llm = llm.bind_tools(tools)
    return llm, system_prompt
