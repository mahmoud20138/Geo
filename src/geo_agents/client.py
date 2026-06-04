"""SDK client for programmatic access to the geo-agents system.

Usage:
    from geo_agents import GeoAgentsSDK

    sdk = GeoAgentsSDK()

    # Run full agent pipeline
    result = await sdk.run("Check weather for drone flight at lat 40.71, lon -74.01")

    # Run with specific skill
    result = await sdk.run_skill("weather_planning", "Check conditions for all drones")

    # Generate plan only
    plan = await sdk.plan("Survey the mining site")

    # Analyze data
    analysis = await sdk.analyze("Temperature readings from sensor-001")

    # List available tools
    tools = sdk.list_tools()

    # List available skills
    skills = sdk.list_skills()

    # Switch LLM provider
    sdk.set_provider("ollama")
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from geo_agents.config import Settings, settings
from geo_agents.state import AgentState, create_initial_state
from geo_agents.graph import agent_graph
from geo_agents.tools.registry import get_all_tools, get_tool_names, get_tools_by_category
from geo_agents.plugins.base import get_registered_plugins, get_plugin_tools
from geo_agents.skills.loader import get_all_skills, get_skill
from geo_agents.mcp.client import get_mcp_servers, get_mcp_tools


@dataclass
class RunResult:
    """Result from an agent pipeline run."""

    response: str
    status: str
    plan: list[str] | None = None
    analysis: dict | None = None
    tool_calls: list[dict] | None = None
    iterations: int = 0
    objective: str = ""

    def to_dict(self) -> dict:
        return {
            "response": self.response,
            "status": self.status,
            "plan": self.plan,
            "analysis": self.analysis,
            "tool_calls": self.tool_calls,
            "iterations": self.iterations,
            "objective": self.objective,
        }


class GeoAgentsSDK:
    """Main SDK entry point for the geo-agents multi-agent system.

    Provides programmatic access to the agent pipeline, tools, skills,
    and MCP integrations without requiring the HTTP server.

    Args:
        provider: LLM provider name ("xiaomi", "ollama", "openrouter").
        config: Optional Settings override.
    """

    def __init__(self, provider: str | None = None, config: Settings | None = None):
        self._config = config or settings
        if provider:
            self._config.provider = provider

    # ── Agent Pipeline ──────────────────────────────────────────

    async def run(self, objective: str, max_iterations: int | None = None) -> RunResult:
        """Run the full agent pipeline (supervisor → planner → executor → analyst).

        Args:
            objective: The user's goal or question.
            max_iterations: Override max iterations for this run.

        Returns:
            RunResult with response, plan, analysis, and tool calls.
        """
        state = create_initial_state(objective)
        result = await agent_graph.ainvoke(state)

        last_message = result["messages"][-1] if result["messages"] else None
        response_text = (
            last_message.content
            if last_message
            else result.get("analysis_results", {}).get("summary", "No response")
        )

        return RunResult(
            response=response_text,
            status=result.get("status", "unknown"),
            plan=result.get("current_plan"),
            analysis=result.get("analysis_results"),
            tool_calls=result.get("execution_results"),
            iterations=result.get("iteration", 0),
            objective=objective,
        )

    async def run_skill(self, skill_name: str, context: str = "") -> RunResult:
        """Run a specific skill by name.

        Args:
            skill_name: Name of the skill to execute.
            context: Additional context for the skill.

        Returns:
            RunResult from the skill execution.
        """
        skill = get_skill(skill_name)
        if not skill:
            return RunResult(
                response=f"Skill not found: {skill_name}",
                status="error",
                objective=context,
            )

        objective = f"[Skill: {skill.name}] {context}" if context else f"[Skill: {skill.name}] Execute with default parameters"
        return await self.run(objective)

    async def plan(self, objective: str) -> list[str]:
        """Generate a plan without executing.

        Args:
            objective: The user's goal.

        Returns:
            List of plan step descriptions.
        """
        from geo_agents.agents.planner import planner_node

        state = create_initial_state(objective)
        result = await planner_node(state)
        return result.get("current_plan", [])

    async def analyze(self, data: str) -> dict:
        """Run analysis on data using the analyst agent.

        Args:
            data: Data or description to analyze.

        Returns:
            Analysis results dict.
        """
        from geo_agents.agents.analyst import analyst_node

        state = create_initial_state(data)
        state["active_agent"] = "analyst"
        state["status"] = "analyzing"
        state["execution_results"] = [{"tool": "direct_input", "result": {"data": data}}]

        result = await analyst_node(state)
        return result.get("analysis_results", {"summary": "No analysis"})

    # ── Tool Management ─────────────────────────────────────────

    def list_tools(self) -> list[dict]:
        """List all available tools with metadata.

        Returns:
            List of tool dicts with name, description, category, source.
        """
        tools = get_all_tools()
        return [
            {
                "name": t.name,
                "description": t.description.split("\n")[0],
            }
            for t in tools
        ]

    def list_tools_by_category(self) -> dict[str, list[dict]]:
        """List tools grouped by category.

        Returns:
            Dict mapping category name to list of tool dicts.
        """
        return get_tools_by_category()

    def get_tool(self, name: str) -> Any | None:
        """Get a specific tool by name.

        Args:
            name: Tool name.

        Returns:
            LangChain tool object or None.
        """
        for t in get_all_tools():
            if t.name == name:
                return t
        return None

    # ── Plugin Management ───────────────────────────────────────

    def list_plugins(self) -> list[dict]:
        """List all loaded plugins.

        Returns:
            List of plugin info dicts.
        """
        plugins = get_registered_plugins()
        return [
            {
                "name": info.name,
                "description": info.description,
                "category": info.category,
                "version": info.version,
            }
            for info in plugins.values()
        ]

    def reload_plugins(self) -> dict:
        """Hot-reload all plugins from configured directories.

        Returns:
            Dict with reload results.
        """
        from geo_agents.plugins.loader import reload_plugins as do_reload
        return do_reload(self._config.plugin_paths)

    # ── Skill Management ────────────────────────────────────────

    def list_skills(self) -> list[dict]:
        """List all available skills.

        Returns:
            List of skill info dicts.
        """
        skills = get_all_skills()
        return [
            {
                "name": s.name,
                "description": s.description,
                "category": s.category,
                "tools": s.tools,
                "steps": s.steps,
            }
            for s in skills.values()
        ]

    def get_skill_info(self, name: str) -> dict | None:
        """Get details of a specific skill.

        Args:
            name: Skill name.

        Returns:
            Skill info dict or None.
        """
        skill = get_skill(name)
        if not skill:
            return None
        return {
            "name": skill.name,
            "description": skill.description,
            "category": skill.category,
            "tools": skill.tools,
            "steps": skill.steps,
            "system_prompt": skill.system_prompt,
        }

    # ── MCP Management ──────────────────────────────────────────

    def list_mcp_servers(self) -> list[dict]:
        """List configured MCP servers.

        Returns:
            List of MCP server info dicts.
        """
        servers = get_mcp_servers()
        return [
            {
                "name": s.name,
                "transport": s.transport,
                "url": s.url,
                "enabled": s.enabled,
            }
            for s in servers.values()
        ]

    def list_mcp_tools(self) -> list[str]:
        """List MCP tool names.

        Returns:
            List of MCP tool names.
        """
        return [t.name for t in get_mcp_tools()]

    # ── Provider Management ─────────────────────────────────────

    def set_provider(self, provider: str) -> dict:
        """Switch the active LLM provider.

        Args:
            provider: Provider name ("xiaomi", "ollama", "openrouter").

        Returns:
            Dict with new provider info.
        """
        if provider not in ["xiaomi", "ollama", "openrouter"]:
            return {"error": f"Unknown provider: {provider}"}
        self._config.provider = provider
        return {
            "provider": provider,
            "model": self._config.llm_model,
            "base_url": self._config.llm_base_url,
        }

    def get_provider(self) -> dict:
        """Get current provider info.

        Returns:
            Dict with current provider details.
        """
        return {
            "provider": self._config.provider,
            "model": self._config.llm_model,
            "base_url": self._config.llm_base_url,
        }

    # ── System Info ─────────────────────────────────────────────

    def status(self) -> dict:
        """Get full system status.

        Returns:
            Dict with system status including counts.
        """
        return {
            "version": "0.2.0",
            "provider": self._config.provider,
            "model": self._config.llm_model,
            "agents": ["supervisor", "planner", "executor", "analyst"],
            "tools": len(get_all_tools()),
            "plugins": len(get_registered_plugins()),
            "skills": len(get_all_skills()),
            "mcp_servers": len(get_mcp_servers()),
            "max_iterations": self._config.max_iterations,
        }
