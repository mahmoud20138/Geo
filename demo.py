"""
Geo-Agents Demo Script
Run this in your CTO meeting to show the system working.

Usage: python demo.py
"""

import asyncio
import json
import sys


def banner(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def load_extensions():
    """Load plugins, skills, MCP on startup."""
    from geo_agents.plugins.loader import discover_plugins
    from geo_agents.skills.loader import load_skills
    from geo_agents.mcp.client import load_mcp_servers
    from geo_agents.config import settings
    discover_plugins(settings.plugin_paths)
    load_skills(settings.skills_paths)
    load_mcp_servers(settings.mcp_config)


async def main():
    load_extensions()
    banner("Geo-Agents SDK Demo")

    # 1. Show system status
    print("1. SYSTEM STATUS")
    print("-" * 40)
    from geo_agents.config import settings
    print(f"   Provider: {settings.provider}")
    print(f"   Model:    {settings.llm_model}")
    print(f"   Port:     {settings.port}")

    # 2. Show tools
    print("\n2. AVAILABLE TOOLS")
    print("-" * 40)
    from geo_agents.tools.registry import get_all_tools, get_tools_by_category
    tools = get_all_tools()
    categories = get_tools_by_category()
    print(f"   Total: {len(tools)} tools")
    for cat, items in categories.items():
        names = [t["name"] for t in items]
        print(f"   {cat}: {', '.join(names)}")

    # 3. Show plugins
    print("\n3. LOADED PLUGINS")
    print("-" * 40)
    from geo_agents.plugins.base import get_registered_plugins
    plugins = get_registered_plugins()
    print(f"   Total: {len(plugins)} plugin tools")
    for name, info in plugins.items():
        print(f"   - {name} ({info.category})")

    # 4. Show skills
    print("\n4. AVAILABLE SKILLS")
    print("-" * 40)
    from geo_agents.skills.loader import get_all_skills
    skills = get_all_skills()
    print(f"   Total: {len(skills)} skills")
    for name, skill in skills.items():
        print(f"   - {name}: {skill.description[:60]}...")

    # 5. Show MCP
    print("\n5. MCP SERVERS")
    print("-" * 40)
    from geo_agents.mcp.client import get_mcp_servers, get_mcp_tool_names
    servers = get_mcp_servers()
    mcp_tools = get_mcp_tool_names()
    print(f"   Servers: {len(servers)}")
    print(f"   Tools:   {len(mcp_tools)}")

    # 6. Run a tool directly
    print("\n6. TOOL EXECUTION DEMO")
    print("-" * 40)
    from geo_agents.tools.external import weather_api
    result = weather_api.invoke({"lat": 40.7128, "lon": -74.0060})
    print(f"   weather_api(lat=40.71, lon=-74.01)")
    print(f"   --> Temperature: {result['temperature']}°C")
    print(f"   --> Conditions:  {result['conditions']}")
    print(f"   --> Wind:        {result['wind_speed']} km/h {result['wind_direction']}")

    # 7. Run a geological plugin
    print("\n7. GEOLOGICAL PLUGIN DEMO")
    print("-" * 40)
    from geo_agents.plugins.base import get_registered_plugins
    plugin_tools = {name: info.func for name, info in get_registered_plugins().items()}
    if "process_drillhole_data" in plugin_tools:
        result = plugin_tools["process_drillhole_data"].invoke({
            "collar_lat": 40.7128, "collar_lon": -74.0060, "collar_elev": 100,
            "depth_from": 150, "depth_to": 300, "dip": -90, "azimuth": 0
        })
        print(f"   process_drillhole_data(depth 150-300m)")
        print(f"   --> Hole ID:    {result['hole_id']}")
        print(f"   --> Midpoint:   lat={result['midpoint']['lat']:.4f}, elev={result['midpoint']['elev']:.1f}m")
    else:
        print("   (plugin not loaded)")

    # 8. RAG demo
    print("\n8. RAG KNOWLEDGE BASE DEMO")
    print("-" * 40)
    try:
        from geo_agents.rag import RAGEngine
        rag = RAGEngine()

        # Ingest
        text = "The copper mineralization occurs at 150-300m depth. Grades: 0.3-1.2% Cu. Controlled by F1 fault."
        chunks = rag.ingest_text(text, source="demo_report.txt")
        print(f"   Ingested: {chunks} chunk(s)")

        # Query
        result = rag.query("What are the copper grades?", n_results=2)
        print(f"   Query:    {result.num_results} result(s)")
        for s in result.sources[:2]:
            print(f"   - {s['source']} (similarity: {s['similarity']:.2f})")
    except ImportError:
        print("   (RAG requires: pip install chromadb sentence-transformers)")

    # 9. Run planner
    print("\n9. PLANNER DEMO (LLM)")
    print("-" * 40)
    from geo_agents.agents.planner import planner_node
    from geo_agents.state import create_initial_state
    state = create_initial_state("Check weather and analyze drillhole data at the ABC mine site")
    result = await planner_node(state)
    plan = result.get("current_plan", [])
    print(f"   Objective: {state['objective']}")
    print(f"   Plan ({len(plan)} steps):")
    for i, step in enumerate(plan, 1):
        print(f"   {i}. {step[:70]}...")

    # 10. Summary
    banner("SUMMARY")
    print(f"   Agents:  4 (supervisor, planner, executor, analyst)")
    print(f"   Tools:   {len(tools)} (core + plugin + MCP + RAG)")
    print(f"   Skills:  {len(skills)}")
    print(f"   Plugins: {len(plugins)}")
    print(f"   MCP:     {len(servers)} servers, {len(mcp_tools)} tools")
    print(f"\n   Dashboard: http://localhost:{settings.port}/")
    print(f"   API Docs:  http://localhost:{settings.port}/docs")
    print(f"   Health:    http://localhost:{settings.port}/health")
    print()


if __name__ == "__main__":
    asyncio.run(main())
