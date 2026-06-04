# Geo-Agents SDK

**Multi-agent orchestration for geospatial digital twin platforms.**

A LangGraph-based system where 4 specialized AI agents collaborate to process geological data, analyze results, and provide insights — extensible via plugins, skills, and MCP servers.

---

## What It Does

```
User: "Check weather for drone flight at lat 40.71, lon -74.01"

→ Supervisor routes to Planner
→ Planner decomposes into 3 steps
→ Executor calls weather_api + get_gps_data
→ Analyst finds patterns and risks
→ Supervisor approves
→ Response returned with plan + data + analysis
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Supervisor    → routes work, reviews results           │
│  Planner       → breaks objectives into tool-mapped steps│
│  Executor      → runs tools (core + plugin + MCP + RAG) │
│  Analyst       → analyzes results for insights          │
└─────────────────────────────────────────────────────────┘
         ↕               ↕               ↕
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Core Tools  │ │   Plugins    │ │  MCP Servers │
│  GIS, DB,    │ │  @register   │ │  stdio, SSE  │
│  Sensors,    │ │  _tool()     │ │  external    │
│  External    │ │  custom.py   │ │  tools       │
└──────────────┘ └──────────────┘ └──────────────┘
                        │
               ┌────────────────┐
               │  RAG Knowledge │
               │  Base (Chroma) │
               │  Historical    │
               │  reports       │
               └────────────────┘
```

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Run tests (59 passing)
pytest tests/ -v

# Start server
python -m uvicorn geo_agents.main:app --port 8084

# Open dashboard
# http://localhost:8084/
```

## SDK Usage

```python
from geo_agents import GeoAgentsSDK

sdk = GeoAgentsSDK()

# Full agent pipeline
result = await sdk.run("Check weather for drone flight")
print(result.response)
print(result.plan)
print(result.tool_calls)

# Plan only
plan = await sdk.plan("Survey the mining site")

# Analyze data
analysis = await sdk.analyze("Temperature readings")

# List tools/skills
tools = sdk.list_tools()      # 28 tools
skills = sdk.list_skills()    # 6 skills
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| POST /api/chat | Full agent pipeline |
| POST /api/plan | Generate plan only |
| POST /api/analyze | Analyze data |
| GET /api/tools | List all tools |
| GET /api/skills | List all skills |
| GET /api/plugins | List plugins |
| GET /api/mcp | List MCP servers |
| GET /api/rag/stats | RAG knowledge base |
| POST /api/rag/ingest | Add documents |
| POST /api/rag/query | Search documents |
| GET /health | Health check |
| GET /metrics | Request metrics |
| GET / | Dashboard |

## Extension System

### Add a Plugin (drop .py in plugins/)

```python
from geo_agents.plugins.base import register_tool

@register_tool(name="my_tool", description="Does X", category="Custom")
def my_tool(param: str) -> dict:
    return {"result": param}
```

### Add a Skill (drop .yaml in skills/)

```yaml
name: my_skill
description: Does something useful
tools: [weather_api, get_gps_data]
system_prompt: |
  You are a specialist in...
steps:
  - Step 1
  - Step 2
```

### Add an MCP Server (edit mcp_servers.json)

```json
{
  "name": "my-server",
  "transport": "stdio",
  "command": "npx",
  "args": ["-y", "@my/mcp-server"],
  "tools": [{"name": "tool1", "description": "..."}]
}
```

### Add RAG (ingest documents)

```python
from geo_agents.rag import RAGEngine

rag = RAGEngine()
rag.ingest_text("Copper grades range from 0.3% to 1.2%...", source="report.txt")
rag.ingest_file("drill_report.pdf")

result = rag.query("What are the copper grades?")
```

## Current Extensions

| Type | Count | Examples |
|------|-------|---------|
| Core Tools | 9 | GIS, Database, Sensors, External |
| Plugins | 9 | Geology (drillhole, block model, hypothesis) |
| Skills | 6 | Weather planning, fleet monitoring, subsurface modeling |
| MCP Servers | 3 | Filesystem, memory, geo-mcp |
| RAG Tools | 3 | Query, ingest, stats |
| **Total** | **28 tools** | |

## Tech Stack

- Python 3.11+
- LangGraph (agent orchestration)
- LangChain (tool abstraction)
- FastAPI (API server)
- ChromaDB (vector storage)
- sentence-transformers (embeddings)

## Project Structure

```
geo-agents/
├── src/geo_agents/
│   ├── __init__.py          # SDK exports
│   ├── client.py            # GeoAgentsSDK
│   ├── config.py            # Multi-provider config
│   ├── state.py             # AgentState
│   ├── graph.py             # LangGraph construction
│   ├── exceptions.py        # Custom errors
│   ├── main.py              # FastAPI server
│   ├── agents/              # 4 agent nodes
│   ├── tools/               # Core + registry
│   ├── plugins/             # Plugin system
│   ├── skills/              # Skill system
│   ├── mcp/                 # MCP integration
│   ├── rag/                 # RAG engine
│   └── api/                 # Routes + WebSocket
├── plugins/                 # User plugins
├── skills/                  # Skill definitions
├── mcp_servers.json         # MCP config
├── dashboard.html           # Web UI
├── tests/                   # 59 tests
└── pyproject.toml
```
