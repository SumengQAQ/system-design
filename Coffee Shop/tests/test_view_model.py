import pytest
from adapters.model import CoffeeMachineStatus, CoffeeTypes, OrderStatus  # type:ignore

CLEAN_REMINDER_THRESHOLD = 5


class TestCoffeeMachineViewModel:
    def test_get_all(self, cm_vm):
        machines = cm_vm.get_all()
        assert len(machines) == 2
        assert machines[0]._serial_number == "CM-001"

    def test_turn_on(self, cm_vm, cm_repo):
        from adapters.model import CoffeeMachine  # type:ignore

        hiber = CoffeeMachine(
            _serial_number="CM-HIB",
            waiting_time=10,
            create_at=0,
            capacity=100.0,
            status=CoffeeMachineStatus.HIBERNATION,
        )
        cm_repo.save(hiber)
        cm_vm.get_all()
        result = cm_vm.turn_on(2)
        assert result is True
        assert cm_vm.get_all()[2].status.value == CoffeeMachineStatus.IDLE.value

    def test_turn_off(self, cm_vm):
        cm_vm.get_all()
        result = cm_vm.turn_off(0)
        assert result is True
        assert cm_vm.get_all()[0].status.value == CoffeeMachineStatus.HIBERNATION.value

    def test_turn_off_working_machine_fails(self, cm_vm):
        cm_vm.get_all()
        cm_vm._coffee_machine_service.change_status(0, CoffeeMachineStatus.WORKING)
        result = cm_vm.turn_off(0)
        assert result is False
        assert cm_vm.get_all()[0].status.value == CoffeeMachineStatus.WORKING.value

    def test_turn_on_fault_machine_fails(self, cm_vm, cm_repo):
        from adapters.model import CoffeeMachine  # type:ignore

        faulty = CoffeeMachine(
            _serial_number="CM-FAIL", waiting_time=10, create_at=0, capacity=100.0, status=CoffeeMachineStatus.FAULT
        )
        cm_repo.save(faulty)
        cm_vm.get_all()
        result = cm_vm.turn_on(2)
        assert result is False

    def test_add_coffee_beans(self, cm_vm):
        result = cm_vm.add_coffee_beans(0, 50.0)
        assert result == 250

    def test_add_coffee_beans_overflow(self, cm_vm, cm_repo):
        from adapters.model import CoffeeMachine  # type:ignore

        full = CoffeeMachine(
            _serial_number="CM-FULL", waiting_time=10, create_at=0, capacity=490.0, status=CoffeeMachineStatus.IDLE
        )
        cm_repo.save(full)
        cm_vm.get_all()
        result = cm_vm.add_coffee_beans(2, 50.0)
        assert result == -1

    @pytest.mark.asyncio
    async def test_make_coffee_invalid_index(self, cm_vm):
        result = await cm_vm.make_coffee(999, 10, CoffeeTypes.LATTE, 15.0, "测试")
        assert result is False

    @pytest.mark.asyncio
    async def test_make_coffee_hibernation(self, cm_vm, cm_repo):
        from adapters.model import CoffeeMachine  # type:ignore

        hiber = CoffeeMachine(
            _serial_number="CM-HIB2",
            waiting_time=10,
            create_at=0,
            capacity=100.0,
            status=CoffeeMachineStatus.HIBERNATION,
        )
        cm_repo.save(hiber)
        cm_vm.get_all()
        result = await cm_vm.make_coffee(2, 10, CoffeeTypes.LATTE, 15.0, "测试")
        assert result is False

    @pytest.mark.asyncio
    async def test_make_coffee_creates_order_and_updates_status(self, cm_vm, order_svc):
        cm_vm.get_all()
        result = await cm_vm.make_coffee(0, 1, CoffeeTypes.LATTE, 15.0, "测试顾客")
        assert result is True

        orders = order_svc.get_all()
        assert len(orders) == 1
        assert orders[0].customer_name == "测试顾客"
        assert orders[0].coffee_type == CoffeeTypes.LATTE
        assert orders[0].status.value == OrderStatus.AWAITING_PICKUP.value

    @pytest.mark.asyncio
    async def test_make_coffee_triggers_clean_reminder(self, cm_vm, cm_repo):
        from adapters.model import CoffeeMachine  # type:ignore

        # 专门为测试准备的咖啡机，连续次数设为 4，再做一次就触发提醒
        machine = CoffeeMachine(
            _serial_number="CM-CLEAN",
            waiting_time=1,
            create_at=0,
            capacity=200.0,
            status=CoffeeMachineStatus.IDLE,
            consecutive_count=4,
        )
        cm_repo.save(machine)
        cm_vm.get_all()

        result = await cm_vm.make_coffee(2, 1, CoffeeTypes.LATTE, 15.0, "测试")
        assert result is True
        cm = cm_vm.get_all()[2]
        assert cm.consecutive_count == CLEAN_REMINDER_THRESHOLD

    @pytest.mark.asyncio
    async def test_make_coffee_no_clean_reminder_below_threshold(self, cm_vm):
        cm_vm.get_all()
        result = await cm_vm.make_coffee(0, 1, CoffeeTypes.LATTE, 15.0, "测试")
        assert result is True
        cm = cm_vm.get_all()[0]
        assert cm.consecutive_count == 1

    def test_clean_resets(self, cm_vm, cm_repo):
        from adapters.model import CoffeeMachine  # type:ignore

        machine = CoffeeMachine(
            _serial_number="CM-DIRTY",
            waiting_time=10,
            create_at=0,
            capacity=200.0,
            status=CoffeeMachineStatus.IDLE,
            consecutive_count=5,
        )
        cm_repo.save(machine)
        cm_vm.get_all()
        result = cm_vm.clean(2)
        assert result is True
        assert cm_vm.get_all()[2].consecutive_count == 0

    def test_clean_invalid_index(self, cm_vm):
        result = cm_vm.clean(999)
        assert result is False

    def test_bind_callback(self, cm_vm):
        called = False

        def cb():
            nonlocal called
            called = True

        cm_vm.bind(cb)
        cm_vm._refresh()
        assert called is True


class TestOrderViewModel:
    def test_finish_order(self, order_vm, order_repo):
        from adapters.model import Order  # type:ignore

        o = Order(customer_name="小明", coffee_type=CoffeeTypes.LATTE)
        order_repo.save(o)
        order_vm.get_all()
        result = order_vm.finish(o.id)
        assert result is True
        order = order_vm._order_service.get_one(o.id)
        assert order.status.value == OrderStatus.COMPLETED.value

    def test_finish_not_found(self, order_vm):
        result = order_vm.finish(999)
        assert result is False

    def test_finish_cancelled(self, order_vm, order_repo):
        from adapters.model import Order  # type:ignore

        o = Order(customer_name="小明", coffee_type=CoffeeTypes.LATTE)
        order_repo.save(o)
        order_vm.get_all()
        order_vm._order_service.change_status(o.id, OrderStatus.CANCELLED)
        result = order_vm.finish(o.id)
        assert result is False

    def test_finish_in_production_rejected(self, order_vm, order_repo):
        from adapters.model import Order  # type:ignore

        o = Order(customer_name="小明", coffee_type=CoffeeTypes.LATTE)
        order_repo.save(o)
        order_vm.get_all()
        order_vm._order_service.change_status(o.id, OrderStatus.IN_PRODUCTION)
        result = order_vm.finish(o.id)
        assert result is False
        order = order_vm._order_service.get_one(o.id)
        assert order.status.value == OrderStatus.IN_PRODUCTION.value

    def test_bind_callback(self, order_vm):
        called = False

        def cb():
            nonlocal called
            called = True

        order_vm.bind(cb)
        order_vm._refresh()
        assert called is True
