"""Tests for the skill system."""

import pytest
from pathlib import Path
from geo_agents.skills.loader import (
    load_skills,
    get_skill,
    get_all_skills,
    get_skill_names,
    clear_skills,
    SkillDefinition,
)


@pytest.fixture(autouse=True)
def clean_skills():
    """Clear skills before and after each test."""
    clear_skills()
    yield
    clear_skills()


def test_load_skills_from_directory():
    """load_skills loads YAML files from the skills directory."""
    loaded = load_skills(["skills"])
    assert len(loaded) >= 1
    assert "weather_planning" in loaded


def test_get_skill():
    """get_skill returns a skill by name."""
    load_skills(["skills"])
    skill = get_skill("weather_planning")
    assert skill is not None
    assert skill.name == "weather_planning"
    assert "weather" in skill.description.lower()


def test_get_skill_fields():
    """Loaded skill has all expected fields."""
    load_skills(["skills"])
    skill = get_skill("weather_planning")
    assert isinstance(skill.tools, list)
    assert len(skill.tools) > 0
    assert isinstance(skill.steps, list)
    assert len(skill.steps) > 0
    assert isinstance(skill.system_prompt, str)
    assert len(skill.system_prompt) > 0


def test_get_all_skills():
    """get_all_skills returns all loaded skills."""
    load_skills(["skills"])
    skills = get_all_skills()
    assert len(skills) >= 1
    assert all(isinstance(s, SkillDefinition) for s in skills.values())


def test_get_skill_names():
    """get_skill_names returns names of all loaded skills."""
    load_skills(["skills"])
    names = get_skill_names()
    assert "weather_planning" in names
    assert "fleet_monitoring" in names
    assert "spatial_analysis" in names


def test_get_nonexistent_skill():
    """get_skill returns None for unknown names."""
    load_skills(["skills"])
    assert get_skill("nonexistent_skill_xyz") is None


def test_clear_skills():
    """clear_skills removes all loaded skills."""
    load_skills(["skills"])
    assert len(get_skill_names()) > 0
    clear_skills()
    assert len(get_skill_names()) == 0


def test_load_skills_nonexistent_dir():
    """load_skills handles nonexistent directories gracefully."""
    loaded = load_skills(["nonexistent_dir_xyz"])
    assert loaded == []


def test_skill_yaml_schema():
    """Verify the YAML schema of example skills."""
    load_skills(["skills"])

    for name in ["weather_planning", "fleet_monitoring", "spatial_analysis"]:
        skill = get_skill(name)
        assert skill is not None, f"Skill {name} not loaded"
        assert skill.name == name
        assert len(skill.description) > 0
        assert len(skill.system_prompt) > 0
        assert isinstance(skill.tools, list)
        assert isinstance(skill.steps, list)
