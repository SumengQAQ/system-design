import asyncio
from typing import Callable

from adapters.model import CoffeeMachine, Order, CoffeeTypes, CoffeeMachineStatus, OrderStatus
from domain.view_model import CoffeeMachineViewModel, OrderViewModel


class CoffeeMachineView:
    def __init__(
        self,
        coffee_machine_view_model: CoffeeMachineViewModel,
        enter: Callable[[str], str],
        output: Callable[[str], None],
    ) -> None:
        self._vm = coffee_machine_view_model
        self._enter = enter
        self._output = output
        self._vm.bind(self._on_data_changed)

    def _on_data_changed(self) -> None:
        pass

    def _choose_machine(self, machines: list[CoffeeMachine]) -> int | None:
        self._output("\n=== 咖啡机列表 ===")
        for i, cm in enumerate(machines):
            status_icon = {
                CoffeeMachineStatus.IDLE: "🟢",
                CoffeeMachineStatus.WORKING: "🟡",
                CoffeeMachineStatus.HIBERNATION: "🔴",
                CoffeeMachineStatus.FAULT: "💀",
            }.get(cm.status, "❓")
            bean_status = f"{cm.capacity:.0f}g" if cm.status != CoffeeMachineStatus.HIBERNATION else "---"
            self._output(
                f"  [{i}] {status_icon} {cm._serial_number} | "
                f"状态: {cm.status.name} | 豆: {bean_status} | 连续: {cm.consecutive_count}杯"
            )
        try:
            idx = int(self._enter("选择咖啡机编号: "))
            if idx < 0 or idx >= len(machines):
                self._output("❌ 编号超出范围！")
                return None
            return idx
        except ValueError:
            self._output("❌ 请输入数字！")
            return None

    def make_coffee(self) -> bool:
        machines = self._vm.get_all()
        idx = self._choose_machine(machines)
        if idx is None:
            return False

        self._output("\n=== 咖啡种类 ===")
        for t in CoffeeTypes:
            self._output(f"  [{t.value}] {t.name}")
        try:
            type_val = int(self._enter("选择咖啡种类编号: "))
            coffee_type = CoffeeTypes(type_val)
        except (ValueError, KeyError):
            self._output("❌ 无效的咖啡种类！")
            return False

        try:
            waiting = int(self._enter("制作时间（秒）: "))
        except ValueError:
            self._output("❌ 请输入数字！")
            return False

        name = self._enter("顾客姓名: ").strip()
        if not name:
            self._output("❌ 姓名不能为空！")
            return False

        asyncio.create_task(self._vm.make_coffee(idx, waiting, coffee_type, 15.0, name))
        return True

    def add_coffee_beans(self) -> bool:
        machines = self._vm.get_all()
        idx = self._choose_machine(machines)
        if idx is None:
            return False

        try:
            grams = float(self._enter("添加咖啡豆重量(g): "))
        except ValueError:
            self._output("❌ 请输入数字！")
            return False

        result = self._vm.add_coffee_beans(idx, grams)
        if result >= 0:
            self._output(f"✅ 添加成功！当前存量: {result}g")
            return True
        return False

    def turn_on(self) -> bool:
        machines = self._vm.get_all()
        idx = self._choose_machine(machines)
        if idx is None:
            return False
        return self._vm.turn_on(idx)

    def turn_off(self) -> bool:
        machines = self._vm.get_all()
        idx = self._choose_machine(machines)
        if idx is None:
            return False
        return self._vm.turn_off(idx)

    def clean(self) -> bool:
        machines = self._vm.get_all()
        idx = self._choose_machine(machines)
        if idx is None:
            return False
        return self._vm.clean(idx)


class OrderView:
    def __init__(
        self,
        order_view_model: OrderViewModel,
        enter: Callable[[str], str],
        output: Callable[[str], None],
    ) -> None:
        self._vm = order_view_model
        self._enter = enter
        self._output = output
        self._vm.bind(self._on_data_changed)

    def _on_data_changed(self) -> None:
        pass

    def list_orders(self) -> list[Order]:
        orders = self._vm.get_all()
        self._output("\n=== 订单列表 ===")
        status_icon = {
            OrderStatus.TO_BE_PRODUCTED: "📋",
            OrderStatus.IN_PRODUCTION: "⚙️",
            OrderStatus.AWAITING_PICKUP: "📦",
            OrderStatus.COMPLETED: "✅",
            OrderStatus.CANCELLED: "❌",
        }
        for o in orders:
            icon = status_icon.get(o.status, "❓")
            self._output(
                f"  {icon} #{o.id} | {o.customer_name} | "
                f"{o.coffee_type.name} | {o.status.name} | {o.create_at.strftime('%H:%M:%S')}"
            )
        return orders

    def finish(self) -> bool:
        self.list_orders()
        try:
            oid = int(self._enter("输入要完成的订单编号: "))
        except ValueError:
            self._output("❌ 请输入数字！")
            return False
        return self._vm.finish(oid)
