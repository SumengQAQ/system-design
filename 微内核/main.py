from core.registry import PluginRegistry
from core.event_bus import EventBus, RightClickEvent
import importlib
import os


def load_all_plugins():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.join(base_dir, "plugins")
    for file_name in os.listdir(plugin_dir):
        if not file_name.endswith(".py") or file_name.startswith("_"):
            continue

        module_name = file_name[:-3]
        importlib.import_module(f"plugins.{module_name}")

    for name in PluginRegistry.get_all():
        PluginRegistry.get(name)().initialize()


def main():
    load_all_plugins()
    print("\n模拟点击右键")
    EventBus.emit(RightClickEvent())


if __name__ == "__main__":
    main()
