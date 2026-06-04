"""Dynamic plugin discovery and loading."""

from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
from geo_agents.plugins.base import get_registered_plugins


def discover_plugins(directories: list[str] | None = None) -> list[str]:
    """Scan directories for Python files and load them as plugins.

    Args:
        directories: List of directory paths to scan. Defaults to ["plugins"].

    Returns:
        List of loaded plugin module names.
    """
    if directories is None:
        directories = ["plugins"]

    loaded = []

    for dir_path in directories:
        path = Path(dir_path)
        if not path.exists():
            continue

        for py_file in sorted(path.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            module_name = f"geo_agents_plugin_{py_file.stem}"
            try:
                _load_module(module_name, py_file)
                loaded.append(module_name)
            except Exception as e:
                print(f"[PluginLoader] Failed to load {py_file}: {e}")

    return loaded


def _load_module(name: str, path: Path) -> None:
    """Load a Python file as a module."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec for {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)


def reload_plugins(directories: list[str] | None = None) -> dict:
    """Reload all plugins from directories.

    Returns:
        Dict with loaded count and plugin names.
    """
    from geo_agents.plugins.base import clear_plugins

    clear_plugins()
    loaded = discover_plugins(directories)
    plugins = get_registered_plugins()

    return {
        "loaded_modules": loaded,
        "plugins": list(plugins.keys()),
        "count": len(plugins),
    }
