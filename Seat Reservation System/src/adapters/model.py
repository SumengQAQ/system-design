from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ReputationScore:
    value: int

    def add_score(self) -> ReputationScore: ...
    def reduce_score(self) -> ReputationScore: ...
    def can_reservation(self) -> bool: ...


@dataclass(kw_only=True, slots=True)
class Student:
    id: str
    name: str
    reputation_score: ReputationScore = ReputationScore(100)


class ReservationStatus(Enum):
    PENDING_CHECK_IN = auto()
    CHECKED_IN = auto()
    ENDED = auto()
    EXPIRED = auto()
    CANCELLED = auto()


class SeatType(Enum):
    QUIET = auto()
    DISCUSSION = auto()
    COMPUTER = auto()


@dataclass(frozen=True, slots=True)
class Position:
    row: int
    column: int


@dataclass(frozen=True, slots=True)
class TimePeriod:
    from_time: datetime
    to_time: datetime

    def extend_time_period(self, to_time: datetime) -> TimePeriod: ...


@dataclass(kw_only=True, slots=True)
class Reservation:
    id: int
    student_id: str
    timer_id: int
    time_period: TimePeriod
    seat_position: Position
    status: ReservationStatus = ReservationStatus.PENDING_CHECK_IN
    temporarily_away_available_time: int = 1800

    def check_in(self) -> None: ...
    def cancel(self) -> None: ...
    def end(self) -> None: ...


@dataclass(kw_only=True, slots=True)
class Seat:
    on_maintain: bool = False
    type: SeatType
    position: Position

    def occupy(self) -> None: ...
    def unoccupy(self) -> None: ...
