"""Skill loading from YAML files."""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SkillDefinition:
    """A loaded skill definition."""

    name: str
    description: str
    system_prompt: str
    tools: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    category: str = "General"
    version: str = "1.0.0"
    source: str = ""  # file path
    metadata: dict[str, Any] = field(default_factory=dict)


# Global skill registry
_skills: dict[str, SkillDefinition] = {}


def load_skills(directories: list[str] | None = None) -> list[str]:
    """Load skill definitions from YAML files in directories.

    Args:
        directories: List of directory paths to scan. Defaults to ["skills"].

    Returns:
        List of loaded skill names.
    """
    if directories is None:
        directories = ["skills"]

    loaded = []

    for dir_path in directories:
        path = Path(dir_path)
        if not path.exists():
            continue

        for yaml_file in sorted(path.glob("*.yaml")) + sorted(path.glob("*.yml")):
            try:
                skill = _load_yaml(yaml_file)
                _skills[skill.name] = skill
                loaded.append(skill.name)
            except Exception as e:
                print(f"[SkillLoader] Failed to load {yaml_file}: {e}")

    return loaded


def _load_yaml(path: Path) -> SkillDefinition:
    """Parse a YAML file into a SkillDefinition."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Expected dict, got {type(data)}")

    required = ["name", "description", "system_prompt"]
    for key in required:
        if key not in data:
            raise ValueError(f"Missing required field: {key}")

    return SkillDefinition(
        name=data["name"],
        description=data["description"],
        system_prompt=data["system_prompt"],
        tools=data.get("tools", []),
        steps=data.get("steps", []),
        category=data.get("category", "General"),
        version=data.get("version", "1.0.0"),
        source=str(path),
        metadata=data.get("metadata", {}),
    )


def get_skill(name: str) -> SkillDefinition | None:
    """Get a skill by name."""
    return _skills.get(name)


def get_all_skills() -> dict[str, SkillDefinition]:
    """Return all loaded skills."""
    return dict(_skills)


def get_skill_names() -> list[str]:
    """Return names of all loaded skills."""
    return list(_skills.keys())


def clear_skills() -> None:
    """Clear all loaded skills (for testing)."""
    _skills.clear()
