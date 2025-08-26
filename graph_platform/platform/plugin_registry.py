from importlib.metadata import entry_points
from typing import Dict, Type
from datasource_api import DataSourcePlugin


def load_plugins() -> Dict[str, Type[DataSourcePlugin]]:
    """
    Discover and load all installed DataSourcePlugin implementations
    via entry points.
    Returns a dict mapping plugin name -> class.
    """
    plugins = {}
    # Look for entry points declared under group "graph_platform.plugins"
    for ep in entry_points(group="graph_platform.plugins"):
        plugin_cls = ep.load()
        if issubclass(plugin_cls, DataSourcePlugin):
            plugins[ep.name] = plugin_cls
    return plugins


# This acts as the Registry (central plugin map).
PLUGINS: Dict[str, Type[DataSourcePlugin]] = load_plugins()


def get_plugin_names():
    """Return list of available plugin names for UI dropdowns."""
    return list(PLUGINS.keys())


def create_plugin(name: str, *args, **kwargs) -> DataSourcePlugin:
    """
    Instantiate a plugin by name from the registry.
    Raises KeyError if not found.
    """
    if name not in PLUGINS:
        raise KeyError(f"Plugin '{name}' not found.")
    return PLUGINS[name](*args, **kwargs)