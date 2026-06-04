from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Provider selection
    provider: str = "xiaomi"  # ollama | xiaomi | openrouter

    # Xiaomi MiMo
    xiaomi_base_url: str = "https://token-plan-sgp.xiaomimimo.com/v1"
    xiaomi_api_key: str = ""
    xiaomi_model: str = "mimo-v2.5-pro"

    # Ollama (local)
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_api_key: str = "not-needed"
    ollama_model: str = "gemma4"

    # OpenRouter
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_api_key: str = ""
    openrouter_model: str = "qwen/qwen3.7-plus"

    # System
    max_iterations: int = 8
    host: str = "0.0.0.0"
    port: int = 8084

    # Extension paths
    plugin_paths: list[str] = ["plugins"]
    skills_paths: list[str] = ["skills"]
    mcp_config: str = "mcp_servers.json"

    model_config = {"env_file": ".env"}

    @property
    def llm_base_url(self) -> str:
        return getattr(self, f"{self.provider}_base_url")

    @property
    def llm_api_key(self) -> str:
        return getattr(self, f"{self.provider}_api_key")

    @property
    def llm_model(self) -> str:
        return getattr(self, f"{self.provider}_model")


settings = Settings()
