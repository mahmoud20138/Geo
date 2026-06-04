"""Skill system for geo-agents.

Skills are high-level capabilities defined in YAML files. Each skill specifies
a name, description, system prompt, required tools, and optional execution steps.

Usage:
    from geo_agents.skills import load_skills, get_skill

    load_skills(["skills"])
    skill = get_skill("weather_planning")
"""

from geo_agents.skills.loader import (
    load_skills,
    get_skill,
    get_all_skills,
    get_skill_names,
    SkillDefinition,
)

__all__ = [
    "load_skills",
    "get_skill",
    "get_all_skills",
    "get_skill_names",
    "SkillDefinition",
]
