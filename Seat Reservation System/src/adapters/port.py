from abc import ABC, abstractmethod
from .model import Student, Seat, Position, Reservation


class StudentRepository(ABC):
    """学生数据库1操作"""

    @abstractmethod
    def save(self, student: Student) -> None: ...
    @abstractmethod
    def get_by_id(self, student_id: str) -> Student: ...
    @abstractmethod
    def get_all(self) -> list[Student]: ...


class SeatRepository(ABC):
    """座位数据库操作"""

    @abstractmethod
    def save(self, seat: Seat) -> None: ...
    @abstractmethod
    def get_by_position(self, position: Position) -> Seat: ...
    @abstractmethod
    def get_all(self) -> list[Seat]: ...


class ReservationRepository(ABC):
    """预约数据库操作"""

    @abstractmethod
    def save(self, reservation: Reservation) -> None: ...
    @abstractmethod
    def get_by_id(self, id: int) -> Reservation: ...
    @abstractmethod
    def get_by_student_id(self, student_id: str) -> list[Reservation]: ...
    @abstractmethod
    def get_by_seat_position(self, position: Position) -> list[Reservation]: ...
    @abstractmethod
    def get_all(self) -> list[Reservation]: ...
