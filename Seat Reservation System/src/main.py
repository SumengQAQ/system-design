from __future__ import annotations
from datetime import datetime, timedelta
from typing import cast

from adapters.model import Student, Seat, SeatType, Position, TimePeriod, ReputationScore
from adapters.service import ReservationService, StudentService, SeatService, StudentSeatReservationService
from domain.memory_repository import MemoryStudentRepository, MemorySeatRepository, MemoryReservationRepository
from domain.timer import TimerManager


def setup_demo_data(
    student_repo: MemoryStudentRepository,
    seat_repo: MemorySeatRepository,
) -> None:
    students: list[Student] = [
        Student(id="S001", name="Alice"),
        Student(id="S002", name="Bob", reputation_score=ReputationScore(70)),
        Student(id="S003", name="Charlie", reputation_score=ReputationScore(50)),
    ]
    for s in students:
        student_repo.save(s)

    seats: list[Seat] = [
        Seat(type=SeatType.QUIET, position=Position(1, 1)),
        Seat(type=SeatType.QUIET, position=Position(1, 2)),
        Seat(type=SeatType.DISCUSSION, position=Position(2, 1)),
        Seat(type=SeatType.DISCUSSION, position=Position(2, 2)),
        Seat(type=SeatType.COMPUTER, position=Position(3, 1)),
        Seat(type=SeatType.COMPUTER, position=Position(3, 2)),
    ]
    for seat in seats:
        seat_repo.save(seat)


def main() -> None:
    student_repo: MemoryStudentRepository = MemoryStudentRepository()
    seat_repo: MemorySeatRepository = MemorySeatRepository()
    reservation_repo: MemoryReservationRepository = MemoryReservationRepository()
    timer_manager: TimerManager = TimerManager()

    setup_demo_data(student_repo, seat_repo)

    reservation_service: ReservationService = ReservationService(reservation_repo, timer_manager)
    student_service: StudentService = StudentService(student_repo)
    seat_service: SeatService = SeatService(seat_repo)

    scheduler_service: StudentSeatReservationService = cast(  # pyright: ignore
        StudentSeatReservationService,  # pyright:ignore
        StudentSeatReservationService(
            reservation_service=reservation_service,
            student_service=student_service,
            seat_service=seat_service,
            timer_manager=timer_manager,
        ),
    )

    now = datetime.now().replace(second=0, microsecond=0)
    # 预约(1,1)座位 14:00~16:00
    tp = TimePeriod(from_time=now + timedelta(hours=1), to_time=now + timedelta(hours=3))

    print(f"Alice 预约座位 (1,1) {tp.from_time.strftime('%H:%M')}~{tp.to_time.strftime('%H:%M')}")
    scheduler_service.reserve("S001", tp, Position(1, 1))
    reservation = reservation_repo.get_by_id(1)
    print(f"  预约id={reservation.id}, 状态={reservation.status.name}")

    print(f"\nAlice 签到")
    scheduler_service.check_in("1")
    reservation = reservation_repo.get_by_id(1)
    print(f"  状态={reservation.status.name}")

    print(f"\nAlice 暂离")
    scheduler_service.temporarily_away("1")
    reservation = reservation_repo.get_by_id(1)
    print(f"  状态={reservation.status.name}")

    print(f"\nAlice 返回")
    scheduler_service.return_from_away("1")
    reservation = reservation_repo.get_by_id(1)
    print(f"  状态={reservation.status.name}")

    print(f"\nAlice 结束自习")
    scheduler_service._reservation_service.end(1)
    reservation = reservation_repo.get_by_id(1)
    print(f"  状态={reservation.status.name}")

    print(f"\nBob 信誉分={student_repo.get_by_id('S002').reputation_score.value}")
    print(f"Bob 信誉分够, 预约座位 (2,1)")
    tp2 = TimePeriod(from_time=now + timedelta(hours=4), to_time=now + timedelta(hours=6))
    scheduler_service.reserve("S002", tp2, Position(2, 1))
    print(f"  预约id=2, 状态={reservation_repo.get_by_id(2).status.name}")

    print(f"\nCharlie 信誉分={student_repo.get_by_id('S003').reputation_score.value}")
    try:
        tp3 = TimePeriod(from_time=now + timedelta(hours=7), to_time=now + timedelta(hours=9))
        scheduler_service.reserve("S003", tp3, Position(2, 2))
        print(f"  ERROR: 应报错")
    except Exception as e:
        print(f"  预约被拒绝: {type(e).__name__}")


if __name__ == "__main__":
    main()
