import asyncio
from typing import Callable

from adapters.model import CoffeeMachine, Order, CoffeeTypes, CoffeeMachineStatus, OrderStatus
from adapters.service import CoffeeMachineService, OrderService
from adapters.exception import (
    CoffeeMachineFaultError,
    CoffeeMachineAlreadyWorkingError,
    CoffeeMachineNotTurnOn,
    InsufficientCoffeeBeansError,
    CoffeeBeanOverflowError,
)

CLEAN_REMINDER_THRESHOLD = 5


class CoffeeMachineViewModel:
    def __init__(
        self,
        coffee_machine_service: CoffeeMachineService,
        order_service: OrderService,
    ) -> None:
        self._coffee_machine_service = coffee_machine_service
        self._order_service = order_service
        self._coffee_machines: list[CoffeeMachine] = []
        self._on_data_change: Callable | None = None

    def bind(self, callable: Callable):
        self._on_data_change = callable

    def get_all(self) -> list[CoffeeMachine]:
        self._coffee_machines = self._coffee_machine_service.get_all()
        return self._coffee_machines

    def _refresh(self) -> None:
        self._coffee_machines = self._coffee_machine_service.get_all()
        if self._on_data_change:
            self._on_data_change()

    async def make_coffee(
        self,
        coffee_machine_index: int,
        waiting_time: int,
        coffee_type: CoffeeTypes,
        grams: float,
        customer_name: str,
    ) -> bool:
        machines = self.get_all()
        if coffee_machine_index < 0 or coffee_machine_index >= len(machines):
            return False

        cm = machines[coffee_machine_index]
        if cm.status != CoffeeMachineStatus.IDLE:
            msg = {
                CoffeeMachineStatus.FAULT: f"☠️ 咖啡机 [{cm._serial_number}] 故障中！",
                CoffeeMachineStatus.WORKING: f"⚙️ 咖啡机 [{cm._serial_number}] 正在工作中～",
                CoffeeMachineStatus.HIBERNATION: f"💤 咖啡机 [{cm._serial_number}] 休眠中，请先开机！",
            }.get(cm.status, "未知状态")
            print(msg)
            return False

        try:
            self._coffee_machine_service.make_coffee(coffee_machine_index, waiting_time)
        except InsufficientCoffeeBeansError:
            print(f"🌱 咖啡豆不足！当前剩余 {cm.capacity:.1f}g，需要 {grams:.1f}g")
            return False
        except (CoffeeMachineFaultError, CoffeeMachineAlreadyWorkingError, CoffeeMachineNotTurnOn) as e:
            print(f"❌ {e}")
            return False

        self._order_service.create(customer_name, coffee_type)
        self._order_service.change_status(self._get_last_order_id(), OrderStatus.IN_PRODUCTION)
        self._refresh()
        print(f"☕ 正在制作 {coffee_type.name}... 预计 {waiting_time} 秒")

        await asyncio.sleep(waiting_time)

        self._order_service.change_status(self._get_last_order_id(), OrderStatus.AWAITING_PICKUP)
        count = self._coffee_machine_service.increace_consecutive_count(coffee_machine_index)
        self._coffee_machine_service.change_status(coffee_machine_index, CoffeeMachineStatus.IDLE)

        if count >= CLEAN_REMINDER_THRESHOLD:
            print(f"🧹 清洁提醒！咖啡机 [{cm._serial_number}] 已连续制作 {count} 杯，请清理！")

        self._refresh()
        print(f"✅ {coffee_type.name} 制作完成！顾客 {customer_name} 请取餐～")
        return True

    def _get_last_order_id(self) -> int:
        orders = self._order_service.get_all()
        last_id = orders[-1].id if orders else None
        return last_id if last_id is not None else 0

    def add_coffee_beans(self, coffee_machine_index: int, grams: float) -> int:
        try:
            return self._coffee_machine_service.add_coffee_beans(coffee_machine_index, grams)
        except CoffeeBeanOverflowError as e:
            print(f"❌ {e}")
            return -1

    def turn_on(self, coffee_machine_index: int) -> bool:
        machines = self.get_all()
        if coffee_machine_index < 0 or coffee_machine_index >= len(machines):
            return False
        cm = machines[coffee_machine_index]
        if cm.status == CoffeeMachineStatus.FAULT:
            print(f"☠️ 咖啡机 [{cm._serial_number}] 故障中，无法开机！")
            return False
        self._coffee_machine_service.change_status(coffee_machine_index, CoffeeMachineStatus.IDLE)
        self._refresh()
        print(f"🔛 咖啡机 [{cm._serial_number}] 已开机")
        return True

    def turn_off(self, coffee_machine_index: int) -> bool:
        machines = self.get_all()
        if coffee_machine_index < 0 or coffee_machine_index >= len(machines):
            return False
        cm = machines[coffee_machine_index]
        if cm.status == CoffeeMachineStatus.WORKING:
            print(f"⛔ 咖啡机 [{cm._serial_number}] 正在制作中，不能关机！")
            return False
        self._coffee_machine_service.turn_off(coffee_machine_index)
        self._refresh()
        print(f"🔌 咖啡机 [{cm._serial_number}] 已休眠")
        return True

    def clean(self, coffee_machine_index: int) -> bool:
        machines = self.get_all()
        if coffee_machine_index < 0 or coffee_machine_index >= len(machines):
            return False
        cm = machines[coffee_machine_index]
        self._coffee_machine_service.clean(coffee_machine_index)
        self._refresh()
        print(f"🧹 咖啡机 [{cm._serial_number}] 已清理，连续计数归零")
        return True


class OrderViewModel:
    def __init__(self, order_service: OrderService) -> None:
        self._order_service = order_service
        self._orders: list[Order] = []
        self._on_data_change: Callable | None = None

    def bind(self, callable: Callable):
        self._on_data_change = callable

    def get_all(self) -> list[Order]:
        self._orders = self._order_service.get_all()
        return self._orders

    def _refresh(self) -> None:
        self._orders = self._order_service.get_all()
        if self._on_data_change:
            self._on_data_change()

    def finish(self, order_id: int) -> bool:
        order = self._order_service.get_one(order_id)
        if order is None:
            print(f"❌ 订单 #{order_id} 不存在！")
            return False
        if order.status == OrderStatus.CANCELLED:
            print(f"❌ 订单 #{order_id} 已取消，无法完成！")
            return False
        if order.status == OrderStatus.IN_PRODUCTION:
            print(f"⏳ 订单 #{order_id} 还在制作中，请稍后再完成～")
            return False
        self._order_service.change_status(order_id, OrderStatus.COMPLETED)
        self._refresh()
        print(f"✅ 订单 #{order_id} 已完成！")
        return True
