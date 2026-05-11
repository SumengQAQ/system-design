from dataclasses import dataclass
from typing import Callable, Any


@dataclass(frozen=True, slots=True)
class Timer:
    id: int
    scan_cycle: int = 30
    waiting_time: int
    time_based_trigger: Callable[[dict], None] = lambda _: None
    time_based_parameter: dict[str, Any]
    final_trigger: Callable[[dict], None] = lambda _: None
    final_parameter: dict[str, Any]

    def scan(self) -> None: ...
    def interrupt(self) -> None: ...
