from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from datetime import datetime, timedelta

from .exception import InvalidReservationStateError, ReputationScoreOutOfRangeError


REPUTATION_SCORE_MIN = 0
REPUTATION_SCORE_MAX = 100
REPUTATION_SCORE_CAN_RESERVATION = 60
RESERVATION_MIN_HOURS = 1
RESERVATION_MAX_HOURS = 4
TEMPORARILY_AWAY_MAX_SECONDS = 1800


@dataclass(frozen=True, slots=True)
class ReputationScore:
    value: int

    def __post_init__(self):
        if not (REPUTATION_SCORE_MIN <= self.value <= REPUTATION_SCORE_MAX):
            raise ReputationScoreOutOfRangeError("Reputation score out of range", self.value, self.value)

    def add_score(self) -> ReputationScore:
        new_value = min(self.value + 1, REPUTATION_SCORE_MAX)
        return ReputationScore(new_value)

    def reduce_score(self, value: int) -> ReputationScore:
        new_value = max(self.value - value, REPUTATION_SCORE_MIN)
        return ReputationScore(new_value)

    def can_reservation(self) -> bool:
        return self.value >= REPUTATION_SCORE_CAN_RESERVATION


@dataclass(kw_only=True, slots=True)
class Student:
    id: str
    name: str
    reputation_score: ReputationScore = ReputationScore(REPUTATION_SCORE_MAX)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class ReservationStatus(Enum):
    PENDING_CHECK_IN = auto()
    CHECKED_IN = auto()
    TEMPORARILY_AWAY = auto()
    ENDED = auto()
    EXPIRED = auto()
    CANCELLED = auto()


_RESERVATION_TRANSITIONS: dict[ReservationStatus, set[ReservationStatus]] = {
    ReservationStatus.PENDING_CHECK_IN: {
        ReservationStatus.CHECKED_IN,
        ReservationStatus.EXPIRED,
        ReservationStatus.CANCELLED,
    },
    ReservationStatus.CHECKED_IN: {
        ReservationStatus.TEMPORARILY_AWAY,
        ReservationStatus.ENDED,
    },
    ReservationStatus.TEMPORARILY_AWAY: {
        ReservationStatus.CHECKED_IN,
        ReservationStatus.EXPIRED,
    },
}


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

    def __post_init__(self):
        if self.from_time > self.to_time:
            raise ValueError("from_time must be <= to_time")
        delta = self.to_time - self.from_time
        if delta < timedelta(hours=RESERVATION_MIN_HOURS):
            raise ValueError(f"Reservation period must be at least {RESERVATION_MIN_HOURS}h")
        if delta > timedelta(hours=RESERVATION_MAX_HOURS):
            raise ValueError(f"Reservation period must be at most {RESERVATION_MAX_HOURS}h")

    def extend_time_period(self, to_time: datetime) -> TimePeriod:
        return TimePeriod(from_time=self.from_time, to_time=to_time)

    def overlaps_with(self, other: TimePeriod) -> bool:
        return self.from_time < other.to_time and other.from_time < self.to_time


@dataclass(kw_only=True, slots=True)
class Reservation:
    id: int
    student_id: str
    timer_id: int
    time_period: TimePeriod
    seat_position: Position
    status: ReservationStatus = ReservationStatus.PENDING_CHECK_IN
    temporarily_away_available_time: int = TEMPORARILY_AWAY_MAX_SECONDS

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Reservation):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def _transition_to(self, target: ReservationStatus) -> None:
        allowed = _RESERVATION_TRANSITIONS.get(self.status)
        if allowed is None or target not in allowed:
            raise InvalidReservationStateError("Invalid reservation state transition", self.status, target)
        self.status = target

    def check_in(self) -> None:
        self._transition_to(ReservationStatus.CHECKED_IN)

    def cancel(self) -> None:
        self._transition_to(ReservationStatus.CANCELLED)

    def end(self) -> None:
        self._transition_to(ReservationStatus.ENDED)

    def expire(self) -> None:
        self._transition_to(ReservationStatus.EXPIRED)

    def temporarily_away(self) -> None:
        self._transition_to(ReservationStatus.TEMPORARILY_AWAY)

    def return_from_away(self) -> None:
        self._transition_to(ReservationStatus.CHECKED_IN)

    def _force_set_status(self, status: ReservationStatus) -> None:
        object.__setattr__(self, "status", status)


@dataclass(kw_only=True, slots=True)
class Seat:
    on_maintain: bool = False
    type: SeatType
    position: Position

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Seat):
            return NotImplemented
        return self.position == other.position

    def __hash__(self) -> int:
        return hash(self.position)
