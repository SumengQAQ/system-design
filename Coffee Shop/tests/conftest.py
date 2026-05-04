import pytest

from domain.repository_memory import MemoryCoffeeMachineRepository, MemoryOrderRepository  # type:ignore
from adapters.service import CoffeeMachineService, OrderService  # type:ignore
from adapters.model import CoffeeMachine, CoffeeMachineStatus  # type:ignore
from domain.view_model import CoffeeMachineViewModel, OrderViewModel  # type:ignore


@pytest.fixture()
def cm_repo():
    return MemoryCoffeeMachineRepository()


@pytest.fixture()
def order_repo():
    return MemoryOrderRepository()


@pytest.fixture()
def demo_machines(cm_repo):
    machines = [
        CoffeeMachine(
            _serial_number="CM-001", waiting_time=30, create_at=0, capacity=200.0, status=CoffeeMachineStatus.IDLE
        ),
        CoffeeMachine(
            _serial_number="CM-002", waiting_time=25, create_at=0, capacity=150.0, status=CoffeeMachineStatus.IDLE
        ),
    ]
    for m in machines:
        cm_repo.save(m)
    return cm_repo


@pytest.fixture()
def cm_svc(demo_machines):
    return CoffeeMachineService(demo_machines)


@pytest.fixture()
def order_svc(order_repo):
    return OrderService(order_repo)


@pytest.fixture()
def cm_vm(cm_svc, order_svc):
    return CoffeeMachineViewModel(cm_svc, order_svc)


@pytest.fixture()
def order_vm(order_svc):
    return OrderViewModel(order_svc)
