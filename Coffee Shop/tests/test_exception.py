from adapters.exception import (  # type:ignore
    OrderExistError,
    OrderNotFoundError,
    CoffeeMachineExistError,
    CoffeeMachineNotFoundError,
    CoffeeMachineFaultError,
    CoffeeMachineAlreadyWorkingError,
    CoffeeMachineNotTurnOn,
    InsufficientCoffeeBeansError,
    CoffeeBeanOverflowError,
)


class TestExceptions:
    def test_order_exist_error(self):
        e = OrderExistError(42)
        assert e.order_id == 42
        assert "42" in str(e)

    def test_order_not_found_error(self):
        e = OrderNotFoundError(1)
        assert e.order_id == 1
        assert "1" in str(e)

    def test_coffee_machine_exist_error(self):
        e = CoffeeMachineExistError("SN-001", 0)
        assert e.serial_number == "SN-001"
        assert e.coffee_machine_index == 0

    def test_coffee_machine_not_found_error(self):
        e = CoffeeMachineNotFoundError("SN-001", 0)
        assert e.serial_number == "SN-001"
        assert e.coffee_machine_index == 0

    def test_coffee_machine_fault_error(self):
        e = CoffeeMachineFaultError("SN-001", 1)
        assert "SN-001" in str(e)
        assert "故障" in str(e)

    def test_coffee_machine_already_working_error(self):
        e = CoffeeMachineAlreadyWorkingError("SN-001", 2)
        assert "工作中" in str(e)

    def test_coffee_machine_not_turn_on(self):
        e = CoffeeMachineNotTurnOn("SN-001", 3)
        assert "未开机" in str(e)

    def test_insufficient_coffee_beans_error(self):
        e = InsufficientCoffeeBeansError("SN-001", 4)
        assert "不足" in str(e)

    def test_coffee_bean_overflow_error(self):
        e = CoffeeBeanOverflowError("SN-001", 5)
        assert "过多" in str(e)
