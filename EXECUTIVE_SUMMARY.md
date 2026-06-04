# Geo-Agents — Executive Summary

## One Sentence

A multi-agent AI system where 4 specialized agents collaborate to process geological data — extensible via plugins, skills, and MCP servers, with trust built into every layer.

## The Problem

Geologists spend weeks manually processing data, building models, and testing hypotheses. Existing AI tools either hallucinate geological features or just do shallow text search.

## The Solution

**The model proposes. The math proves.**

4 agents work together:
- **Supervisor** — Routes and validates
- **Planner** — Breaks objectives into steps
- **Executor** — Runs deterministic tools
- **Analyst** — Finds patterns with confidence scores

## What's Different

| Others | Geo-Agents |
|--------|------------|
| LLM invents coordinates | Python computes coordinates |
| No confidence scores | Every output has confidence |
| Fixed functionality | Extensible via plugins |
| Single model | 3 providers, switch at runtime |
| Just RAG | RAG + deterministic computation |

## Current State

- 28 tools (core + plugin + MCP + RAG)
- 6 pre-built skills
- 9 geological plugins
- 59 tests passing
- Full dashboard with live demos
- SDK for programmatic access

## Key Talking Points

1. **Trust** — Never invents data, always has sources
2. **Extensible** — Add tools without code changes
3. **Scalable** — Async pipeline, hot-reload, multi-provider
4. **Production-ready** — Tests, metrics, logging, error handling

## Demo

```bash
python demo.py          # Show all components
# Open http://localhost:8084/
# Click Live Demos → run any demo
```

## Files

| File | Purpose |
|------|---------|
| `REPORT.md` | Full technical report |
| `PITCH.md` | Talking points for CTO |
| `README.md` | Documentation |
| `demo.py` | Live demo script |
| `dashboard.html` | Visual dashboard |

---

*"Prompts are temporary. Architecture is permanent."*
