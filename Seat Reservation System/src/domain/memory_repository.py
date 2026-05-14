from adapters.port import StudentRepository, SeatRepository, ReservationRepository
from adapters.model import Student, Seat, Reservation, Position, TimePeriod
from adapters.exception import ResourceNotFoundError


class MemoryStudentRepository(StudentRepository):
    def __init__(self, students: dict[str, Student] | None = None):
        self._students: dict[str, Student] = students or {}

    def save(self, student: Student) -> None:
        self._students[student.id] = student

    def get_by_id(self, student_id: str) -> Student:
        student = self._students.get(student_id)
        if student is None:
            raise ResourceNotFoundError(f"Student {student_id} not found")
        return student

    def get_all(self) -> list[Student]:
        return list(self._students.values())


class MemorySeatRepository(SeatRepository):
    def __init__(self, seats: dict[Position, Seat] | None = None):
        self._seats: dict[Position, Seat] = seats or {}

    def save(self, seat: Seat) -> None:
        self._seats[seat.position] = seat

    def get_by_position(self, position: Position) -> Seat:
        seat = self._seats.get(position)
        if seat is None:
            raise ResourceNotFoundError(f"Seat at {position} not found")
        return seat

    def get_all(self) -> list[Seat]:
        return list(self._seats.values())


class MemoryReservationRepository(ReservationRepository):
    def __init__(self, reservations: dict[int, Reservation] | None = None):
        self._reservations: dict[int, Reservation] = reservations or {}

    def save(self, reservation: Reservation) -> None:
        self._reservations[reservation.id] = reservation

    def get_by_id(self, id: int) -> Reservation:
        reservation = self._reservations.get(id)
        if reservation is None:
            raise ResourceNotFoundError(f"Reservation {id} not found")
        return reservation

    def get_by_student_id(self, student_id: str) -> list[Reservation]:
        return [r for r in self._reservations.values() if r.student_id == student_id]

    def get_by_seat_position(self, position: Position) -> list[Reservation]:
        return [r for r in self._reservations.values() if r.seat_position == position]

    def get_by_time_period(self, time_period: TimePeriod) -> list[Reservation]:
        return [r for r in self._reservations.values() if r.time_period.overlaps_with(time_period)]

    def get_all(self) -> list[Reservation]:
        return list(self._reservations.values())
