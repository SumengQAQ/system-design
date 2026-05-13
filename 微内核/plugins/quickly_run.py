from core.registry import BasePlugin
from core.event_bus import EventBus, RightClickEvent


class QuicklyRunPlugin(BasePlugin):
    """在点击右键的时候，打印一个“> 编译并运行”选项"""

    name = "quickly_run"

    @classmethod
    def initialize(cls):
        EventBus.register(RightClickEvent, cls.show_option)
        print("快速运行插件初始化")

    @staticmethod
    def show_option(right_click_event: RightClickEvent):
        print("> 编译并运行")
