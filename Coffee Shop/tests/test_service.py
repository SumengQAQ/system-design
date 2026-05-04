import pytest
from adapters.model import CoffeeMachineStatus, CoffeeTypes, OrderStatus  # type:ignore
from adapters.exception import (  # type:ignore
    CoffeeMachineFaultError,
    CoffeeMachineAlreadyWorkingError,
    CoffeeMachineNotTurnOn,
    InsufficientCoffeeBeansError,
    CoffeeBeanOverflowError,
)


class TestCoffeeMachineService:
    def test_make_coffee_success(self, cm_svc):
        cm_svc.get_all()
        result = cm_svc.make_coffee(0, 30)
        assert result is True
        cm = cm_svc.get_all()[0]
        assert cm.status.value == CoffeeMachineStatus.WORKING.value
        assert cm.capacity == 185.0

    def test_make_coffee_fault(self, cm_svc, cm_repo):
        from adapters.model import CoffeeMachine  # type:ignore

        faulty = CoffeeMachine(
            _serial_number="CM-FAULT", waiting_time=10, create_at=0, capacity=100.0, status=CoffeeMachineStatus.FAULT
        )
        cm_repo.save(faulty)
        cm_svc.get_all()
        with pytest.raises(CoffeeMachineFaultError):
            cm_svc.make_coffee(2, 10)

    def test_make_coffee_hibernation(self, cm_svc, cm_repo):
        from adapters.model import CoffeeMachine  # type:ignore

        hiber = CoffeeMachine(
            _serial_number="CM-HIB",
            waiting_time=10,
            create_at=0,
            capacity=100.0,
            status=CoffeeMachineStatus.HIBERNATION,
        )
        cm_repo.save(hiber)
        cm_svc.get_all()
        with pytest.raises(CoffeeMachineNotTurnOn):
            cm_svc.make_coffee(2, 10)

    def test_make_coffee_already_working(self, cm_svc):
        cm_svc.get_all()
        cm_svc.make_coffee(0, 30)
        with pytest.raises(CoffeeMachineAlreadyWorkingError):
            cm_svc.make_coffee(0, 30)

    def test_make_coffee_insufficient_beans(self, cm_svc, cm_repo):
        from adapters.model import CoffeeMachine  # type:ignore

        empty = CoffeeMachine(
            _serial_number="CM-EMPTY", waiting_time=10, create_at=0, capacity=5.0, status=CoffeeMachineStatus.IDLE
        )
        cm_repo.save(empty)
        cm_svc.get_all()
        with pytest.raises(InsufficientCoffeeBeansError):
            cm_svc.make_coffee(2, 10)

    def test_add_coffee_beans(self, cm_svc):
        cm_svc.get_all()
        result = cm_svc.add_coffee_beans(0, 50.0)
        assert result == 250

    def test_add_coffee_beans_overflow(self, cm_svc, cm_repo):
        from adapters.model import CoffeeMachine  # type:ignore

        near_full = CoffeeMachine(
            _serial_number="CM-FULL", waiting_time=10, create_at=0, capacity=490.0, status=CoffeeMachineStatus.IDLE
        )
        cm_repo.save(near_full)
        cm_svc.get_all()
        with pytest.raises(CoffeeBeanOverflowError):
            cm_svc.add_coffee_beans(2, 20.0)

    def test_cost_coffee_beans(self, cm_svc):
        cm_svc.get_all()
        result = cm_svc.cost_coffee_beans(0, 30.0)
        assert result == 170

    def test_cost_coffee_beans_insufficient(self, cm_svc):
        cm_svc.get_all()
        with pytest.raises(InsufficientCoffeeBeansError):
            cm_svc.cost_coffee_beans(0, 999.0)

    def test_change_status(self, cm_svc):
        cm_svc.get_all()
        cm_svc.change_status(0, CoffeeMachineStatus.FAULT)
        assert cm_svc.get_all()[0].status.value == CoffeeMachineStatus.FAULT.value

    def test_turn_off(self, cm_svc):
        cm_svc.get_all()
        cm_svc.turn_off(0)
        assert cm_svc.get_all()[0].status.value == CoffeeMachineStatus.HIBERNATION.value

    def test_increace_consecutive_count(self, cm_svc):
        cm_svc.get_all()
        assert cm_svc.increace_consecutive_count(0) == 1
        assert cm_svc.increace_consecutive_count(0) == 2

    def test_clean_resets_consecutive_count(self, cm_svc):
        cm_svc.get_all()
        cm_svc.increace_consecutive_count(0)
        cm_svc.increace_consecutive_count(0)
        assert cm_svc.get_all()[0].consecutive_count == 2
        cm_svc.clean(0)
        assert cm_svc.get_all()[0].consecutive_count == 0

    def test_get_one(self, cm_svc):
        found = cm_svc.get_one("CM-001")
        assert found is not None
        assert found._serial_number == "CM-001"

    def test_get_one_not_found(self, cm_svc):
        assert cm_svc.get_one("NOT-EXIST") is None


class TestOrderService:
    def test_create(self, order_svc):
        result = order_svc.create("小明", CoffeeTypes.LATTE)
        assert result is True
        orders = order_svc.get_all()
        assert len(orders) == 1
        assert orders[0].customer_name == "小明"

    def test_get_all(self, order_svc):
        order_svc.create("A", CoffeeTypes.LATTE)
        order_svc.create("B", CoffeeTypes.AMERICANO)
        assert len(order_svc.get_all()) == 2

    def test_change_status(self, order_svc):
        order_svc.create("小明", CoffeeTypes.LATTE)
        order_svc.change_status(1, OrderStatus.IN_PRODUCTION)
        order = order_svc.get_one(1)
        assert order is not None
        assert order.status.value == OrderStatus.IN_PRODUCTION.value

    def test_get_one(self, order_svc):
        order_svc.create("小明", CoffeeTypes.LATTE)
        found = order_svc.get_one(1)
        assert found is not None
        assert found.customer_name == "小明"

    def test_get_one_not_found(self, order_svc):
        assert order_svc.get_one(999) is None
