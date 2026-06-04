# Geo-Agents SDK
## Subsurface Reasoning Engine — Technical Report

**Version:** 0.2.0
**Date:** June 2026
**Author:** Mahmoud Elshafei

---

## Executive Summary

Geo-Agents is a multi-agent orchestration SDK built for geospatial digital twin platforms. It uses 4 specialized AI agents to process geological data, analyze results, and provide validated insights — extensible via plugins, skills, and MCP servers.

The system is designed around one core principle: **trust over speed**. A geologist can tolerate a slow system. A geologist cannot tolerate a system that confidently invents a fault line or mineralized zone.

**Key differentiator:** The LLM proposes hypotheses. Deterministic Python computes geometry. The model never invents coordinates, grades, or geological boundaries.

---

## The Problem

### Current State of Geological Software

| Pain Point | Impact |
|------------|--------|
| Manual wireframing | Weeks per iteration |
| Specialist queue | Management can't test ideas |
| Software operators | Geologists spend time on UI, not interpretation |
| No reasoning layer | Data exists but isn't synthesized |
| Slow hypothesis testing | Ideas die in queue |

### The AI Trap

Most AI systems for geology make one of two mistakes:

1. **Too creative** — The LLM invents geological features that don't exist in the data
2. **Too shallow** — Just RAG over documents, no actual computation

Neither approach produces results a geologist can trust.

---

## The Solution

### Architecture: The Model Proposes, The Math Proves

```
┌─────────────────────────────────────────────────────────────┐
│                    Supervisor Agent                          │
│         Routes work · Reviews results · Validates           │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
    ┌──────────▼──────────┐       ┌───────────▼───────────┐
    │    Planner Agent     │       │    Analyst Agent       │
    │  Decomposes into     │       │  Finds patterns        │
    │  tool-mapped steps   │       │  Confidence scores     │
    └──────────┬───────────┘       └───────────┬────────────┘
               │                               │
    ┌──────────▼──────────────────────────────────────────┐
    │                 Executor Agent                        │
    │  Runs tools per step · Deterministic results          │
    │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐  │
    │  │ Core    │ │ Plugin  │ │ MCP     │ │ RAG        │  │
    │  │ 9 tools │ │ 9 tools │ │ 7 tools │ │ Knowledge  │  │
    │  └─────────┘ └─────────┘ └─────────┘ └───────────┘  │
    └──────────────────────────────────────────────────────┘
```

### Separation of Concerns

| Layer | Responsibility | Example |
|-------|---------------|---------|
| **Reasoning** | Suggest hypotheses | "Copper grades may improve at depth near F1 fault" |
| **Retrieval** | Collect relevant data | Query drillhole database, ingest historical reports |
| **Computation** | Run deterministic calculations | Process drillhole coordinates, calculate areas, build surfaces |
| **Validation** | Challenge hypotheses | Test geological hypothesis against data, confidence scoring |

The LLM handles reasoning and planning. Python handles computation and validation. Neither oversteps.

---

## What Makes It Different

### 1. Trust by Design

| Traditional AI | Geo-Agents |
|---------------|------------|
| LLM generates coordinates | Python computes coordinates |
| LLM invents grades | Tools return real data |
| Black box output | Every result has a source |
| No confidence scores | Confidence on every analysis |
| "Drill here" | "Drill here because these 5 indicators agree" |

### 2. Extension System (No Code Changes)

| Extension Type | How It Works | Example |
|---------------|-------------|---------|
| **Plugins** | Drop .py in plugins/ | `@register_tool` decorator |
| **Skills** | Drop .yaml in skills/ | Pre-built workflows |
| **MCP** | Edit mcp_servers.json | External tool servers |
| **RAG** | Ingest documents | Historical reports |

Add new geological tools without touching the agent layer.

### 3. Multi-Provider Architecture

| Provider | Model | Use Case |
|----------|-------|----------|
| Xiaomi MiMo | mimo-v2.5-pro | Primary reasoning |
| Ollama | gemma4, llama3.2 | Local/offline |
| OpenRouter | qwen/qwen3.7-plus | Fallback |

Switch providers at runtime. The orchestration layer never changes.

### 4. Geological Domain Knowledge

Built-in tools for geological workflows:

| Tool | Category | Purpose |
|------|----------|---------|
| `process_drillhole_data` | Geology | 3D coordinate calculation |
| `build_subsurface_surface` | Geology | Triangulated surface construction |
| `generate_block_model` | Geology | Regularized block model |
| `extract_report_metadata` | Geology | NLP extraction from reports |
| `test_geological_hypothesis` | Geology | Confidence scoring |
| `calculate_volume` | Geology | Volume between surfaces |
| `query_geojson` | GIS | Spatial queries |
| `get_satellite_imagery` | GIS | Remote sensing metadata |
| `calculate_area` | GIS | Polygon area calculation |

### 5. RAG for Geological Knowledge

Not just text search — geological entity extraction:

```python
# Traditional RAG
results = vector_store.search("copper grades")
# Returns: paragraphs of text

# Geo-Agents RAG
result = rag.query("What are the copper grades at depth?")
# Returns: structured sources with similarity scores
# Each source: {source, similarity, text_preview, metadata}
```

The system extracts:
- Rock formations
- Depth intervals
- Fault references
- Mineralization descriptions
- Coordinates
- Historical interpretations

Instead of storing text, we store geological knowledge.

---

## Technical Deep Dive

### Agent Pipeline

```
Request → Supervisor → Planner → Executor → Analyst → Supervisor → Response
                ↑                                          │
                └──────────── Validation Loop ─────────────┘
```

**Max iterations:** 8 (configurable)
**Average latency:** 10-30 seconds (depends on LLM provider)

### Tool Registry

Tools are merged at runtime from 4 sources:

```python
def get_all_tools():
    tools = []
    tools += get_core_tools()      # 9 built-in tools
    tools += get_plugin_tools()    # 9 plugin tools
    tools += get_mcp_tools()       # 7 MCP tools
    tools += get_rag_tools()       # 3 RAG tools
    return deduplicate(tools)      # 28 total
```

### Plugin System

```python
# plugins/my_geology_tool.py
from geo_agents.plugins.base import register_tool

@register_tool(name="my_tool", description="...", category="Geology")
def my_tool(param: str) -> dict:
    """Deterministic computation — not LLM."""
    return {"result": computed_value}
```

Auto-discovered on startup. Hot-reloadable via API.

### Skill System

```yaml
# skills/my_workflow.yaml
name: my_workflow
description: Does something useful
tools: [weather_api, get_gps_data, process_drillhole_data]
system_prompt: |
  You are a geological specialist...
steps:
  - Get GPS positions
  - Check weather conditions
  - Process drillhole data
```

### RAG Engine

```python
from geo_agents.rag import RAGEngine

rag = RAGEngine()

# Ingest historical reports
rag.ingest_file("drill_report_1985.pdf")
rag.ingest_text("Copper grades range from 0.3% to 1.2%...", source="report.txt")

# Query with similarity scoring
result = rag.query("What are the copper grades?", n_results=5)
# Returns: {answer, sources, query, num_results}
```

---

## Benefits

### For Geologists

| Benefit | Impact |
|---------|--------|
| Minutes instead of weeks | Faster iteration on hypotheses |
| Confidence scores | Know when to trust the output |
| Source attribution | Every result traces back to data |
| Natural language interface | No software training needed |
| Hypothesis testing | Test ideas without specialist queue |

### For Management

| Benefit | Impact |
|---------|--------|
| Self-service exploration | Test ideas without waiting |
| Audit trail | Every recommendation has evidence |
| Scalable | Add tools without code changes |
| Cost efficient | Local models via Ollama |
| Production ready | 59 tests, metrics, logging |

### For Engineering

| Benefit | Impact |
|---------|--------|
| Modular architecture | Each agent is independent |
| Extension system | Plugins, skills, MCP, RAG |
| Multi-provider | Switch LLMs without code changes |
| Async pipeline | High throughput |
| Full SDK | Programmatic + API access |

---

## Use Cases

### 1. Exploration Geology

**Question:** "Where should I drill next?"

**Pipeline:**
1. Planner decomposes into: get drillholes, query faults, retrieve assays, calculate targets
2. Executor calls: get_gps_data, query_geojson, query_postgres, calculate_area
3. Analyst finds: grade trends, structural controls, geophysical correlations
4. Supervisor validates: are data sources sufficient? confidence high enough?

**Output:**
```json
{
  "recommendation": "Drill at intersection of F1 fault and IP anomaly",
  "confidence": 0.78,
  "evidence": [
    "Grade increases below 150m near F1",
    "IP anomaly extends 800m along strike",
    "Historical hole DH-85-012: 15m at 2.1% Cu from 180m"
  ]
}
```

### 2. Historical Report Processing

**Problem:** 20-year-old PDF reports sitting unread.

**Solution:**
```python
# Ingest
rag.ingest_file("exploration_report_2004.pdf")

# Query
result = rag.query("What faults were identified in the 2004 survey?")
```

The system extracts geological entities, not just text chunks.

### 3. Fleet Monitoring

**Question:** "Are all drones operational?"

**Pipeline:**
1. Get GPS positions of all assets
2. Collect telemetry from sensors
3. Check for anomalies (low battery, offline sensors)
4. Generate fleet health report

### 4. Weather-Aware Flight Planning

**Question:** "Can I fly the drone today?"

**Pipeline:**
1. Get drone GPS positions
2. Check weather at each location
3. Assess wind speed and visibility
4. Provide GO/NO-GO recommendation per drone

---

## Comparison with Traditional Approaches

| Aspect | Traditional Software | Single LLM | Geo-Agents |
|--------|---------------------|------------|------------|
| Speed | Weeks | Seconds | Minutes |
| Trust | High (manual) | Low (hallucination) | High (validated) |
| Extensibility | Low | N/A | High (plugins) |
| Cost | High (specialists) | Low | Low |
| Accuracy | High (human) | Variable | High (computed) |
| Scalability | Low | High | High |
| Auditability | Low | None | Full (evidence trail) |

---

## Current Capabilities

| Component | Count | Details |
|-----------|-------|---------|
| Agents | 4 | Supervisor, Planner, Executor, Analyst |
| Core Tools | 9 | GIS, Database, Sensors, External |
| Plugin Tools | 9 | Geology (drillhole, surface, block model, hypothesis) |
| MCP Tools | 7 | Filesystem, memory, geo-mcp |
| RAG Tools | 3 | Query, ingest, stats |
| Skills | 6 | Weather, fleet, spatial, subsurface, hypothesis, reports |
| MCP Servers | 3 | Configured and ready |
| Tests | 59 | All passing |
| API Endpoints | 25+ | REST + WebSocket |
| LLM Providers | 3 | Xiaomi, Ollama, OpenRouter |

---

## Roadmap

### Phase 1: Current (Proof of Concept)
- [x] Multi-agent orchestration
- [x] Plugin/skill/MCP/RAG system
- [x] Geological tools
- [x] Dashboard with live demos
- [x] SDK for programmatic access

### Phase 2: Real Data Integration
- [ ] Replace mock tools with real GIS/DB connections
- [ ] PostGIS integration for spatial queries
- [ ] Real drillhole database
- [ ] Production RAG with real reports

### Phase 3: 3D Visualization
- [ ] Cesium integration for 3D rendering
- [ ] Subsurface model visualization
- [ ] Real-time telemetry overlay

### Phase 4: Production Deployment
- [ ] Authentication and authorization
- [ ] Rate limiting and quotas
- [ ] Persistent state management
- [ ] Monitoring and alerting

---

## Technical Specifications

| Spec | Value |
|------|-------|
| Language | Python 3.11+ |
| Agent Framework | LangGraph |
| Tool Framework | LangChain |
| API Framework | FastAPI |
| Vector Store | ChromaDB |
| Embeddings | all-MiniLM-L6-v2 |
| LLM Providers | Xiaomi MiMo, Ollama, OpenRouter |
| Test Framework | pytest (async) |
| License | MIT |

---

## Contact

**Mahmoud Elshafei**
- Multi-Agent Systems
- Computational Linguistics
- RAG / NLP
- FastAPI / vLLM

---

*"Prompts are temporary. Architecture is permanent."*
