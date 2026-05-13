from core.registry import BasePlugin
from core.event_bus import EventBus, RightClickEvent


class FormatPlugin(BasePlugin):
    """在点击右键的时候，打印一个“> 格式化”选项"""

    name = "format"

    @classmethod
    def initialize(cls):
        EventBus.register(RightClickEvent, cls.show_option)
        print("格式化插件初始化")

    @staticmethod
    def show_option(right_click_event: RightClickEvent) -> None:
        print("> 格式化")
