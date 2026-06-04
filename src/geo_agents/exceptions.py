"""Custom exceptions for the geo-agents SDK."""


class GeoAgentsError(Exception):
    """Base exception for all geo-agents errors."""
    pass


class ProviderError(GeoAgentsError):
    """LLM provider connection or configuration error."""
    pass


class ToolExecutionError(GeoAgentsError):
    """Tool execution failed."""
    def __init__(self, tool_name: str, message: str, args: dict | None = None):
        self.tool_name = tool_name
        self.args = args or {}
        super().__init__(f"Tool '{tool_name}' failed: {message}")


class PluginLoadError(GeoAgentsError):
    """Plugin loading failed."""
    def __init__(self, plugin_path: str, message: str):
        self.plugin_path = plugin_path
        super().__init__(f"Plugin '{plugin_path}' failed to load: {message}")


class SkillNotFoundError(GeoAgentsError):
    """Requested skill does not exist."""
    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        super().__init__(f"Skill not found: {skill_name}")


class MCPConnectionError(GeoAgentsError):
    """MCP server connection failed."""
    def __init__(self, server_name: str, message: str):
        self.server_name = server_name
        super().__init__(f"MCP server '{server_name}' connection failed: {message}")


class MaxIterationsError(GeoAgentsError):
    """Agent pipeline exceeded maximum iterations."""
    def __init__(self, max_iterations: int):
        self.max_iterations = max_iterations
        super().__init__(f"Pipeline exceeded {max_iterations} iterations without converging")


class GraphBuildError(GeoAgentsError):
    """LangGraph graph construction failed."""
    pass


class ConfigValidationError(GeoAgentsError):
    """Configuration validation failed."""
    pass
