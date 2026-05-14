from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any
from threading import Timer as ThreadingTimer


@dataclass(frozen=True, slots=True)
class Timer:
    id: int
    waiting_time: int
    time_based_parameter: dict[str, Any]
    final_parameter: dict[str, Any]
    time_based_trigger: Callable[[dict], None] = lambda _: None
    final_trigger: Callable[[dict], None] = lambda _: None
    scan_cycle: int = 30


class TimerManager:
    def __init__(self):
        self._timers: dict[int, Timer] = {}
        self._threads: dict[int, ThreadingTimer] = {}
        self._next_id: int = 0
        self._interrupted: set[int] = set()

    def create_timer(
        self,
        waiting_time: int,
        final_trigger: Callable[[dict], None],
        final_parameter: dict[str, Any],
        time_based_trigger: Callable[[dict], None] | None = None,
        time_based_parameter: dict[str, Any] | None = None,
        scan_cycle: int = 30,
    ) -> Timer:
        timer_id = self._next_id
        self._next_id += 1
        timer = Timer(
            id=timer_id,
            waiting_time=waiting_time,
            time_based_trigger=time_based_trigger or (lambda _: None),
            time_based_parameter=time_based_parameter or {},
            final_trigger=final_trigger,
            final_parameter=final_parameter,
            scan_cycle=scan_cycle,
        )
        self._timers[timer_id] = timer
        return timer

    def start_timer(self, timer_id: int) -> None:
        timer = self._timers.get(timer_id)
        if timer is None:
            return
        self._interrupted.discard(timer_id)

        def _run():
            if timer_id in self._interrupted:
                return
            timer.final_trigger(timer.final_parameter)

        t = ThreadingTimer(timer.waiting_time, _run)
        self._threads[timer_id] = t
        t.start()

    def interrupt(self, timer_id: int) -> None:
        self._interrupted.add(timer_id)
        thread = self._threads.pop(timer_id, None)
        if thread:
            thread.cancel()

    def remove_timer(self, timer_id: int) -> None:
        self.interrupt(timer_id)
        self._timers.pop(timer_id, None)
