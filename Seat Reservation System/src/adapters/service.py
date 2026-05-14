from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any
from .port import ReservationRepository, StudentRepository, SeatRepository
from .model import (
    TimePeriod,
    Position,
    Reservation,
    ReservationStatus,
    Student,
    ReputationScore,
    Seat,
)
from .exception import ResourceNotFoundError, InvalidReservationStateError, InvalidSeatStateError
from domain.command import Command
from domain.timer import TimerManager


CHECK_IN_TIMEOUT_SECONDS: int = 1800
TEMPORARILY_AWAY_TIMEOUT_SECONDS: int = 1800
REPUTATION_SCORE_REDUCE_ON_EXPIRE: int = 10
REPUTATION_SCORE_INCREASE_CYCLE_SECONDS: int = 1800


class ReservationService:
    _repository: ReservationRepository
    _timer_manager: TimerManager

    def __init__(self, repository: ReservationRepository, timer_manager: TimerManager) -> None:
        self._repository = repository
        self._timer_manager = timer_manager

    def reserve(self, student_id: str, time_period: TimePeriod, seat_position: Position) -> Reservation:
        reservations: list[Reservation] = self._repository.get_by_seat_position(seat_position)
        for r in reservations:
            if r.status in (
                ReservationStatus.PENDING_CHECK_IN,
                ReservationStatus.CHECKED_IN,
                ReservationStatus.TEMPORARILY_AWAY,
            ):
                if r.time_period.overlaps_with(time_period):
                    raise InvalidSeatStateError("Seat already reserved in this time period", r.status, "RESERVED")
        reservation_id: int = len(self._repository.get_all()) + 1
        timer: Any = self._timer_manager.create_timer(
            waiting_time=CHECK_IN_TIMEOUT_SECONDS,
            final_trigger=self._handle_no_show,
            final_parameter={"reservation_id": reservation_id},
        )
        reservation: Reservation = Reservation(
            id=reservation_id,
            student_id=student_id,
            timer_id=timer.id,
            time_period=time_period,
            seat_position=seat_position,
        )
        self._repository.save(reservation)
        self._timer_manager.start_timer(timer.id)
        return reservation

    def _handle_no_show(self, params: dict[str, Any]) -> None:
        reservation_id: int = params["reservation_id"]
        try:
            reservation: Reservation = self._repository.get_by_id(reservation_id)
        except ResourceNotFoundError:
            return
        if reservation.status == ReservationStatus.PENDING_CHECK_IN:
            reservation.expire()
            self._repository.save(reservation)

    def _handle_away_timeout(self, params: dict[str, Any]) -> None:
        reservation_id: int = params["reservation_id"]
        try:
            reservation: Reservation = self._repository.get_by_id(reservation_id)
        except ResourceNotFoundError:
            return
        if reservation.status == ReservationStatus.TEMPORARILY_AWAY:
            reservation.expire()
            self._repository.save(reservation)

    def check_in(self, id: int) -> None:
        reservation: Reservation = self._repository.get_by_id(id)
        reservation.check_in()
        self._timer_manager.interrupt(reservation.timer_id)
        study_timer: Any = self._timer_manager.create_timer(
            waiting_time=int((reservation.time_period.to_time - datetime.now()).total_seconds()),
            final_trigger=self._handle_study_end,
            final_parameter={"reservation_id": id},
        )
        self._timer_manager.start_timer(study_timer.id)
        object.__setattr__(reservation, "timer_id", study_timer.id)
        self._repository.save(reservation)

    def _handle_study_end(self, params: dict[str, Any]) -> None:
        reservation_id: int = params["reservation_id"]
        try:
            reservation: Reservation = self._repository.get_by_id(reservation_id)
        except ResourceNotFoundError:
            return
        if reservation.status in (ReservationStatus.CHECKED_IN, ReservationStatus.TEMPORARILY_AWAY):
            reservation.end()
            self._repository.save(reservation)

    def countdown_begin(self, id: int) -> None:
        reservation: Reservation = self._repository.get_by_id(id)
        self._timer_manager.interrupt(reservation.timer_id)
        timer: Any = self._timer_manager.create_timer(
            waiting_time=CHECK_IN_TIMEOUT_SECONDS,
            final_trigger=self._handle_no_show,
            final_parameter={"reservation_id": id},
        )
        self._timer_manager.start_timer(timer.id)
        object.__setattr__(reservation, "timer_id", timer.id)
        self._repository.save(reservation)

    def countdown_end(self, id: int) -> None:
        reservation: Reservation = self._repository.get_by_id(id)
        self._timer_manager.interrupt(reservation.timer_id)

    def cancel(self, id: int) -> None:
        reservation: Reservation = self._repository.get_by_id(id)
        reservation.cancel()
        self._timer_manager.interrupt(reservation.timer_id)
        self._repository.save(reservation)

    def end(self, id: int) -> None:
        reservation: Reservation = self._repository.get_by_id(id)
        reservation.end()
        self._timer_manager.interrupt(reservation.timer_id)
        self._repository.save(reservation)

    def extend_time_period(self, id: int, seconds: int) -> None:
        reservation: Reservation = self._repository.get_by_id(id)
        new_to_time: datetime = reservation.time_period.to_time + timedelta(seconds=seconds)
        new_time_period: TimePeriod = reservation.time_period.extend_time_period(new_to_time)
        self._timer_manager.interrupt(reservation.timer_id)
        new_timer: Any = self._timer_manager.create_timer(
            waiting_time=int((new_to_time - datetime.now()).total_seconds()),
            final_trigger=self._handle_study_end,
            final_parameter={"reservation_id": id},
        )
        self._timer_manager.start_timer(new_timer.id)
        object.__setattr__(reservation, "time_period", new_time_period)
        object.__setattr__(reservation, "timer_id", new_timer.id)
        self._repository.save(reservation)


class StudentService:
    _repository: StudentRepository

    def __init__(self, repository: StudentRepository) -> None:
        self._repository = repository

    def add_reputation_score(self, id: str, value: int) -> None:
        student: Student = self._repository.get_by_id(id)
        new_score: ReputationScore = student.reputation_score
        for _ in range(value):
            new_score = new_score.add_score()
        object.__setattr__(student, "reputation_score", new_score)
        self._repository.save(student)

    def reduce_reputation_score(self, id: str, value: int) -> None:
        student: Student = self._repository.get_by_id(id)
        new_score: ReputationScore = student.reputation_score.reduce_score(value)
        object.__setattr__(student, "reputation_score", new_score)
        self._repository.save(student)


class SeatService:
    _repository: SeatRepository

    def __init__(self, repository: SeatRepository) -> None:
        self._repository = repository

    def occupy(self, position: Position) -> None:
        seat: Seat = self._repository.get_by_position(position)
        if seat.on_maintain:
            raise InvalidSeatStateError("Seat is under maintenance", seat.on_maintain, False)
        self._repository.save(seat)

    def unoccupy(self, position: Position) -> None:
        self._repository.get_by_position(position)

    def maintain(self, position: Position) -> None:
        seat: Seat = self._repository.get_by_position(position)
        object.__setattr__(seat, "on_maintain", True)
        self._repository.save(seat)

    def fix(self, position: Position) -> None:
        seat: Seat = self._repository.get_by_position(position)
        object.__setattr__(seat, "on_maintain", False)
        self._repository.save(seat)


@Command
class StudentSeatReservationService:
    _reservation_service: ReservationService
    _student_service: StudentService
    _seat_service: SeatService
    _timer_manager: TimerManager

    def __init__(
        self,
        reservation_service: ReservationService,
        student_service: StudentService,
        seat_service: SeatService,
        timer_manager: TimerManager,
    ) -> None:
        self._reservation_service = reservation_service
        self._student_service = student_service
        self._seat_service = seat_service
        self._timer_manager = timer_manager

    def reserve(self, student_id: str, time_period: TimePeriod, seat_position: Position) -> None:
        self._student_service.add_reputation_score(student_id, 0)
        student: Student = self._student_service._repository.get_by_id(student_id)
        if not student.reputation_score.can_reservation():
            raise InvalidReservationStateError(
                "Student reputation score too low", student.reputation_score.value, "RESERVE"
            )
        self._reservation_service.reserve(student_id, time_period, seat_position)

    def reserve_undo(self, student_id: str, time_period: TimePeriod, seat_position: Position) -> None:
        reservations: list[Reservation] = self._reservation_service._repository.get_by_seat_position(seat_position)
        for r in reservations:
            if (
                r.student_id == student_id
                and r.time_period == time_period
                and r.status == ReservationStatus.PENDING_CHECK_IN
            ):
                self._reservation_service.cancel(r.id)
                break

    def check_in(self, reservation_id: str) -> None:
        self._reservation_service.check_in(int(reservation_id))

    def check_in_undo(self, reservation_id: str) -> None:
        rid: int = int(reservation_id)
        reservation: Reservation = self._reservation_service._repository.get_by_id(rid)
        reservation._force_set_status(ReservationStatus.PENDING_CHECK_IN)
        self._timer_manager.interrupt(reservation.timer_id)
        check_in_timer: Any = self._timer_manager.create_timer(
            waiting_time=CHECK_IN_TIMEOUT_SECONDS,
            final_trigger=self._reservation_service._handle_no_show,
            final_parameter={"reservation_id": rid},
        )
        self._timer_manager.start_timer(check_in_timer.id)
        object.__setattr__(reservation, "timer_id", check_in_timer.id)
        self._reservation_service._repository.save(reservation)

    def extend_time_period(self, reservation_id: str, seconds: int) -> None:
        self._reservation_service.extend_time_period(int(reservation_id), seconds)

    def extend_time_period_undo(self, reservation_id: str, seconds: int) -> None:
        rid: int = int(reservation_id)
        reservation: Reservation = self._reservation_service._repository.get_by_id(rid)
        original_to: datetime = reservation.time_period.to_time - timedelta(seconds=seconds)
        original_time_period: TimePeriod = reservation.time_period.extend_time_period(original_to)
        self._timer_manager.interrupt(reservation.timer_id)
        study_timer: Any = self._timer_manager.create_timer(
            waiting_time=int((original_to - datetime.now()).total_seconds()),
            final_trigger=self._reservation_service._handle_study_end,
            final_parameter={"reservation_id": rid},
        )
        self._timer_manager.start_timer(study_timer.id)
        object.__setattr__(reservation, "time_period", original_time_period)
        object.__setattr__(reservation, "timer_id", study_timer.id)
        self._reservation_service._repository.save(reservation)

    def temporarily_away(self, reservation_id: str) -> None:
        rid: int = int(reservation_id)
        reservation: Reservation = self._reservation_service._repository.get_by_id(rid)
        reservation.temporarily_away()
        self._timer_manager.interrupt(reservation.timer_id)
        away_timer: Any = self._timer_manager.create_timer(
            waiting_time=TEMPORARILY_AWAY_TIMEOUT_SECONDS,
            final_trigger=self._reservation_service._handle_away_timeout,
            final_parameter={"reservation_id": rid},
        )
        self._timer_manager.start_timer(away_timer.id)
        object.__setattr__(reservation, "timer_id", away_timer.id)
        self._reservation_service._repository.save(reservation)

    def temporarily_away_undo(self, reservation_id: str) -> None:
        rid: int = int(reservation_id)
        reservation: Reservation = self._reservation_service._repository.get_by_id(rid)
        reservation._force_set_status(ReservationStatus.CHECKED_IN)
        self._timer_manager.interrupt(reservation.timer_id)
        remaining: int = int((reservation.time_period.to_time - datetime.now()).total_seconds())
        if remaining > 0:
            study_timer: Any = self._timer_manager.create_timer(
                waiting_time=remaining,
                final_trigger=self._reservation_service._handle_study_end,
                final_parameter={"reservation_id": rid},
            )
            self._timer_manager.start_timer(study_timer.id)
            object.__setattr__(reservation, "timer_id", study_timer.id)
        self._reservation_service._repository.save(reservation)

    def return_from_away(self, reservation_id: str) -> None:
        rid: int = int(reservation_id)
        reservation: Reservation = self._reservation_service._repository.get_by_id(rid)
        reservation.return_from_away()
        self._timer_manager.interrupt(reservation.timer_id)
        remaining: int = int((reservation.time_period.to_time - datetime.now()).total_seconds())
        if remaining > 0:
            study_timer: Any = self._timer_manager.create_timer(
                waiting_time=remaining,
                final_trigger=self._reservation_service._handle_study_end,
                final_parameter={"reservation_id": rid},
            )
            self._timer_manager.start_timer(study_timer.id)
            object.__setattr__(reservation, "timer_id", study_timer.id)
        self._reservation_service._repository.save(reservation)

    def return_from_away_undo(self, reservation_id: str) -> None:
        rid: int = int(reservation_id)
        reservation: Reservation = self._reservation_service._repository.get_by_id(rid)
        reservation._force_set_status(ReservationStatus.TEMPORARILY_AWAY)
        self._timer_manager.interrupt(reservation.timer_id)
        away_timer: Any = self._timer_manager.create_timer(
            waiting_time=TEMPORARILY_AWAY_TIMEOUT_SECONDS,
            final_trigger=self._reservation_service._handle_away_timeout,
            final_parameter={"reservation_id": rid},
        )
        self._timer_manager.start_timer(away_timer.id)
        object.__setattr__(reservation, "timer_id", away_timer.id)
        self._reservation_service._repository.save(reservation)

    def auto_increase_reputation(self, student_id: str) -> None:
        self._student_service.add_reputation_score(student_id, 1)
