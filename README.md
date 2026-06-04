# Geo-Agents SDK

**Multi-agent orchestration for geospatial digital twin platforms.**

A LangGraph-based system where 4 specialized AI agents collaborate to process geological data, analyze results, and provide validated insights — extensible via plugins, skills, and MCP servers.

---

## Dashboard Preview

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Geo-Agents                    [Operational] [xiaomi/mimo-v2.5-pro]     │
├──────────────────────────────────────────────────────────────────────────┤
│  [Overview] [Architecture] [Extensions] [Live Demos] [Agent Chat] [API] │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │  Agents: 4  │ │ Tools: 28   │ │ Skills: 6   │ │ Tests: 59   │       │
│  │  Supervisor │ │ Core + Plugin│ │ Pre-built   │ │ All passing │       │
│  │  Planner    │ │ MCP + RAG   │ │ workflows   │ │             │       │
│  │  Executor   │ │             │ │             │ │             │       │
│  │  Analyst    │ │             │ │             │ │             │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  🏗️ Architecture Principles                                │         │
│  │                                                            │         │
│  │  The model proposes. The math proves.                      │         │
│  │                                                            │         │
│  │  • LLM suggests hypotheses                                │         │
│  │  • Python computes geometry                               │         │
│  │  • Never invents coordinates or grades                    │         │
│  │  • Confidence scores on every output                      │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## What This Project Solves

### Problem 1: Manual Software Operation

```
BEFORE (Traditional Workflow):
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Open      │    │   Manually  │    │   Build     │    │   Export    │
│   Software  │───▶│   Draw      │───▶│   Surfaces  │───▶│   Model     │
│             │    │   Faults    │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     2 hours           4 hours           3 hours           1 hour
                        Total: 10+ hours

AFTER (Geo-Agents):
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Type      │    │   Agents    │    │   Results   │
│   "Build    │───▶│   Execute   │───▶│   Returned  │
│   model"    │    │   Tools     │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
    10 seconds        30 seconds         Instant
                        Total: < 1 minute
```

### Problem 2: Hallucination in Geological AI

```
Traditional AI:
┌─────────────┐         ┌─────────────┐
│    LLM      │────────▶│  "Drill at  │
│  (Creative) │         │  lat 40.71" │  ← INVENTED! No data supports this.
└─────────────┘         └─────────────┘

Geo-Agents:
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    LLM      │────────▶│   Python    │────────▶│  "Drill at  │
│ (Reasoning) │         │   Tools     │         │  lat 40.71" │  ← COMPUTED from data.
└─────────────┘         └─────────────┘         └─────────────┘
  "Maybe near              Process drillhole        "Because 5
   F1 fault?"              data, query DB           indicators agree"
```

### Problem 3: Slow Hypothesis Testing

```
Traditional:
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Submit  │    │   Wait   │    │  Review  │    │  Iterate │
│  Request │───▶│  2 weeks │───▶│  Results │───▶│  (again) │
└──────────┘    └──────────┘    └──────────┘    └──────────┘

Geo-Agents:
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Type    │    │  Agents  │    │  Results │
│  Idea    │───▶│  Gather  │───▶│  with    │
│          │    │  Data    │    │  Confidence│
└──────────┘    └──────────┘    └──────────┘
  10 seconds      30 seconds      Instant
```

---

## Architecture

### Agent Flow

```
User: "Where should I drill next?"
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        SUPERVISOR                                │
│              Routes work · Reviews results · Validates          │
└──────┬─────────────────────────────────────────────────────┬────┘
       │                                                     │
       ▼                                                     ▼
┌──────────────┐                                  ┌──────────────┐
│   PLANNER    │                                  │    END       │
│  Decompose   │                                  │  (Approve)   │
│  into steps  │                                  └──────────────┘
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                       EXECUTOR                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Core Tools│ │ Plugins  │ │   MCP    │ │   RAG    │       │
│  │ 9 tools  │ │ 9 tools  │ │ 7 tools  │ │ Knowledge│       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│         ▲                                                   │
│         │ invoke                                            │
│         └───────────────────────────────────────────────────│
└──────┬──────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│   ANALYST    │
│  Find risks  │───────▶ Confidence: 0.78
│  Patterns    │         "Drill at F1 × IP anomaly"
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  SUPERVISOR  │───────▶ VALIDATE ───────▶ Return to user
└──────────────┘
```

### Tool Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    MERGED TOOL REGISTRY                      │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  CORE (9)   │  │ PLUGIN (9)  │  │   MCP (7)   │        │
│  │             │  │             │  │             │        │
│  │ query_geo   │  │ drillhole   │  │ read_file   │        │
│  │ satellite   │  │ subsurface  │  │ write_file  │        │
│  │ area_calc   │  │ block_model │  │ list_dir    │        │
│  │ postgres    │  │ hypothesis  │  │ search      │        │
│  │ timeseries  │  │ geocode     │  │ geocode     │        │
│  │ telemetry   │  │ distance    │  │ entities    │        │
│  │ gps_data    │  │ tides       │  │ pois        │        │
│  │ weather     │  │ report_nlp  │  │             │        │
│  │ traffic     │  │ volume      │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  RAG (3) — ChromaDB + sentence-transformers         │   │
│  │  rag_query · rag_ingest_text · rag_stats            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Live Example: Full Pipeline

### Request

```bash
curl -X POST http://localhost:8084/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Check weather for drone flight at lat 40.71, lon -74.01"}'
```

### Response

```json
{
  "response": "Weather conditions at the drone location (40.71, -74.01) show...",
  "status": "complete",
  "plan": [
    "Get GPS location of drone asset",
    "Check weather at drone coordinates",
    "Assess flight safety based on wind and visibility"
  ],
  "tool_calls": [
    {
      "tool": "get_gps_data",
      "args": {"asset_id": "asset-001"},
      "result": {
        "lat": 40.7128,
        "lon": -74.006,
        "altitude": 10.5,
        "speed": 0.0,
        "heading": 180.0
      }
    },
    {
      "tool": "weather_api",
      "args": {"lat": 40.71, "lon": -74.01},
      "result": {
        "temperature": 18.5,
        "humidity": 72,
        "wind_speed": 12.3,
        "wind_direction": "NW",
        "conditions": "partly_cloudy",
        "visibility_km": 10.0,
        "forecast": "Clear skies expected in the next 6 hours"
      }
    }
  ],
  "analysis": {
    "summary": "Weather conditions are suitable for drone flight...",
    "patterns": ["Wind speed below threshold", "Good visibility"],
    "risks": ["Humidity slightly high"],
    "recommendations": ["Proceed with flight planning"],
    "confidence": 0.85
  },
  "iterations": 3
}
```

---

## Live Example: Geological Plugin

### Drillhole Processing

```python
from geo_agents.plugins.base import get_registered_plugins

tools = {name: info.func for name, info in get_registered_plugins().items()}
result = tools["process_drillhole_data"].invoke({
    "collar_lat": 40.7128,
    "collar_lon": -74.0060,
    "collar_elev": 100,
    "depth_from": 150,
    "depth_to": 300,
    "dip": -90,
    "azimuth": 0
})
```

### Output

```json
{
  "hole_id": "DH-40712--74006",
  "collar": {
    "lat": 40.7128,
    "lon": -74.006,
    "elev": 100
  },
  "interval": {
    "from": 150,
    "to": 300,
    "length": 150
  },
  "midpoint": {
    "lat": 40.7128,
    "lon": -74.006,
    "elev": -125.0
  },
  "dip": -90,
  "azimuth": 0
}
```

---

## Live Example: RAG Knowledge Base

### Ingest Historical Report

```bash
curl -X POST http://localhost:8084/api/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The copper mineralization at the ABC deposit occurs at depths between 150-300m. Grades range from 0.3% to 1.2% Cu. The F1 fault system controls the mineralization.",
    "source": "drill_report_2024.txt"
  }'
```

### Response

```json
{
  "chunks_created": 1,
  "source": "drill_report_2024.txt",
  "status": "ingested"
}
```

### Query

```bash
curl -X POST http://localhost:8084/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the copper grades at depth?", "n_results": 3}'
```

### Response

```json
{
  "answer": "[1] (source: drill_report_2024.txt, similarity: 0.60)\nThe copper mineralization occurs at depths between 150-300m...",
  "sources": [
    {
      "source": "drill_report_2024.txt",
      "similarity": 0.601,
      "text_preview": "The copper mineralization at the ABC deposit..."
    },
    {
      "source": "geological_survey_1985.txt",
      "similarity": 0.473,
      "text_preview": "Historical drilling intersected 15m at 2.1% Cu..."
    }
  ],
  "query": "What are the copper grades at depth?",
  "num_results": 3
}
```

---

## Live Example: Plan Generation

```bash
curl -X POST http://localhost:8084/api/demo/plan
```

### Response

```json
{
  "demo": "plan_generation",
  "objective": "Survey the copper deposit at ABC mine, check weather, and analyze drillhole data",
  "plan": [
    "Step 1: Use get_gps_data to obtain GPS coordinates of drillholes at ABC mine",
    "Step 2: Use weather_api to check weather conditions at the mine site",
    "Step 3: Use query_postgres to retrieve historical drillhole assay data",
    "Step 4: Use calculate_area to compute the survey area coverage"
  ],
  "steps_count": 4
}
```

---

## SDK Usage

### Basic Usage

```python
from geo_agents import GeoAgentsSDK

sdk = GeoAgentsSDK()

# Full agent pipeline
result = await sdk.run("Check weather for drone flight")
print(result.response)
print(result.plan)
print(result.tool_calls)
```

### Plan Only

```python
plan = await sdk.plan("Survey the mining site")
# Returns: ["Step 1: Get GPS...", "Step 2: Query database...", ...]
```

### Analyze Data

```python
analysis = await sdk.analyze("Temperature readings from sensor-001")
# Returns: {"summary": "...", "patterns": [...], "risks": [...]}
```

### Run Specific Skill

```python
result = await sdk.run_skill("weather_planning", "Check conditions for all drones")
```

### List Tools and Skills

```python
tools = sdk.list_tools()      # 28 tools
skills = sdk.list_skills()    # 6 skills
```

---

## Extension System

### Add a Plugin

Drop a `.py` file in `plugins/`:

```python
# plugins/my_geology_tool.py
from geo_agents.plugins.base import register_tool

@register_tool(name="analyze_core_sample", description="Analyze drill core sample data", category="Geology")
def analyze_core_sample(depth_from: float, depth_to: float, rock_type: str) -> dict:
    """Analyze core sample and return lithological description."""
    # Deterministic computation — not LLM
    return {
        "depth_from": depth_from,
        "depth_to": depth_to,
        "rock_type": rock_type,
        "description": f"Core sample from {depth_from}m to {depth_to}m: {rock_type}",
        "confidence": 0.95
    }
```

### Add a Skill

Drop a `.yaml` file in `skills/`:

```yaml
# skills/drill_targeting.yaml
name: drill_targeting
description: Identify optimal drill targets based on geological data
category: Geology
tools:
  - query_geojson
  - query_postgres
  - process_drillhole_data
  - test_geological_hypothesis
system_prompt: |
  You are a drill targeting specialist.
  Analyze geological data to identify the best drill targets.
  Consider: structural controls, grade trends, geophysical anomalies.
  Always provide confidence scores and evidence.
steps:
  - Query geological fault data from GIS layers
  - Retrieve historical drillhole assay results
  - Process drillhole coordinates to 3D
  - Test hypothesis about structural controls
  - Rank targets by confidence and evidence
```

### Add an MCP Server

Edit `mcp_servers.json`:

```json
{
  "servers": [
    {
      "name": "my-geo-server",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@my/geo-mcp-server"],
      "tools": [
        {
          "name": "reverse_geocode",
          "description": "Convert lat/lon to address",
          "input_schema": {
            "type": "object",
            "properties": {
              "lat": {"type": "number"},
              "lon": {"type": "number"}
            }
          }
        }
      ]
    }
  ]
}
```

---

## API Endpoints

### Agent Pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Full agent pipeline with LLM |
| POST | `/api/mission` | Alias for /chat |
| POST | `/api/plan` | Generate plan only |
| POST | `/api/analyze` | Run analyst only |

### Tools & Extensions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tools` | List all 28 tools |
| GET | `/api/plugins` | List 9 plugins |
| GET | `/api/skills` | List 6 skills |
| GET | `/api/mcp` | List MCP servers |
| GET | `/api/extensions` | All extensions summary |

### RAG

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rag/stats` | Knowledge base statistics |
| POST | `/api/rag/ingest` | Add documents |
| POST | `/api/rag/query` | Search documents |
| POST | `/api/rag/clear` | Clear knowledge base |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Request metrics |
| GET | `/api/status` | System status |
| GET | `/api/providers` | LLM providers |
| POST | `/api/providers/{name}` | Switch provider |
| GET | `/` | Dashboard |

### Live Demos

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/demo/weather-check` | Weather at drone locations |
| POST | `/api/demo/fleet-status` | GPS + telemetry |
| POST | `/api/demo/spatial-query` | GIS + area calculation |
| POST | `/api/demo/plan` | Plan generation |
| POST | `/api/demo/analyze` | Data analysis |
| POST | `/api/demo/skill-run` | Skill execution |
| POST | `/api/demo/rag-ingest` | RAG ingest |
| POST | `/api/demo/rag-query` | RAG query |
| POST | `/api/demo/tools-list` | Tools inventory |
| POST | `/api/demo/plugins-reload` | Hot-reload plugins |
| POST | `/api/demo/database-query` | Database query |
| POST | `/api/demo/sensor-telemetry` | Sensor telemetry |

---

## Current Extensions

### Tools (28 total)

| Category | Count | Tools |
|----------|-------|-------|
| GIS | 5 | query_geojson, get_satellite_imagery, calculate_area, geocode_address, calculate_distance |
| Database | 2 | query_postgres, query_timeseries |
| Sensors | 2 | get_telemetry, get_gps_data |
| External | 3 | weather_api, traffic_api, noaa_tides |
| Geology | 6 | process_drillhole_data, build_subsurface_surface, generate_block_model, extract_report_metadata, test_geological_hypothesis, calculate_volume |
| MCP | 7 | read_file, write_file, list_directory, create_entities, search_nodes, reverse_geocode, find_nearby_pois |
| RAG | 3 | rag_query, rag_ingest_text, rag_stats |

### Skills (6 total)

| Skill | Category | Description |
|-------|----------|-------------|
| weather_planning | Operations | Check weather for drone flight safety |
| fleet_monitoring | Operations | Monitor all tracked assets |
| spatial_analysis | GIS | GIS spatial analysis |
| subsurface_modeling | Geology | Build subsurface models from drillhole data |
| hypothesis_testing | Geology | Test geological hypotheses |
| report_ingestion | Data | Ingest historical reports |

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Agent Framework | LangGraph | Multi-agent orchestration |
| Tool Framework | LangChain | Tool abstraction and binding |
| API Server | FastAPI | REST API + WebSocket |
| Vector Store | ChromaDB | RAG knowledge base |
| Embeddings | sentence-transformers | Document embedding |
| LLM Providers | Xiaomi MiMo, Ollama, OpenRouter | Multi-provider support |
| Testing | pytest (async) | 59 tests |

---

## Project Structure

```
geo-agents/
├── src/geo_agents/
│   ├── __init__.py          # SDK exports
│   ├── client.py            # GeoAgentsSDK class
│   ├── config.py            # Multi-provider configuration
│   ├── state.py             # AgentState TypedDict
│   ├── graph.py             # LangGraph construction
│   ├── exceptions.py        # Custom error types
│   ├── main.py              # FastAPI server + middleware
│   ├── agents/
│   │   ├── supervisor.py    # Route & review
│   │   ├── planner.py       # Decompose objectives
│   │   ├── executor.py      # Run tools
│   │   └── analyst.py       # Analyze results
│   ├── tools/
│   │   ├── registry.py      # Merge all tool sources
│   │   ├── gis.py           # GIS tools
│   │   ├── database.py      # Database tools
│   │   ├── sensors.py       # Sensor tools
│   │   └── external.py      # External API tools
│   ├── plugins/
│   │   ├── base.py          # @register_tool decorator
│   │   └── loader.py        # Dynamic discovery
│   ├── skills/
│   │   └── loader.py        # YAML skill loading
│   ├── mcp/
│   │   └── client.py        # MCP server integration
│   ├── rag/
│   │   ├── engine.py        # RAG engine
│   │   ├── chunker.py       # Document chunking
│   │   └── store.py         # ChromaDB vector store
│   └── api/
│       ├── routes.py        # REST endpoints
│       └── websocket.py     # WebSocket manager
├── plugins/                 # User plugins (auto-discovered)
│   ├── example_plugin.py    # Example: geocode, distance, tides
│   └── geology_plugin.py    # Geological tools
├── skills/                  # Skill definitions (YAML)
│   ├── weather_planning.yaml
│   ├── fleet_monitoring.yaml
│   ├── spatial_analysis.yaml
│   ├── subsurface_modeling.yaml
│   ├── hypothesis_testing.yaml
│   └── report_ingestion.yaml
├── mcp_servers.json         # MCP server configuration
├── dashboard.html           # Web dashboard
├── demo.py                  # Demo script
├── tests/                   # 59 tests
├── pyproject.toml           # Project config
├── README.md                # This file
├── REPORT.md                # Technical report
├── PITCH.md                 # CTO talking points
└── EXECUTIVE_SUMMARY.md     # One-page summary
```

---

## What Still Needs Work

### Gap 1: Traceability

**Current:** Returns analysis with sources.
**Needed:** Citation engine linking conclusions to specific report pages.

### Gap 2: Geospatial Guardrails

**Current:** Tools return deterministic results.
**Needed:** Validation layer blocking physically impossible models.

### Gap 3: Vanilla RAG Limitations

**Current:** Vector similarity search over text chunks.
**Needed:** Graph RAG with entity extraction and PostGIS integration.

---

*"The model proposes. The math proves."*
