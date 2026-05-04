import asyncio
from domain.repository_memory import MemoryCoffeeMachineRepository, MemoryOrderRepository
from adapters.service import CoffeeMachineService, OrderService
from adapters.model import CoffeeMachine, CoffeeMachineStatus
from domain.view_model import CoffeeMachineViewModel, OrderViewModel
from domain.view import CoffeeMachineView, OrderView


def terminal_enter(prompt: str) -> str:
    return input(prompt)


def terminal_output(message: str) -> None:
    print(message)


async def main():
    cm_repo = MemoryCoffeeMachineRepository()
    order_repo = MemoryOrderRepository()

    demo_machines = [
        CoffeeMachine(
            _serial_number="CM-001", waiting_time=30, create_at=0, capacity=200.0, status=CoffeeMachineStatus.IDLE
        ),
        CoffeeMachine(
            _serial_number="CM-002", waiting_time=25, create_at=0, capacity=150.0, status=CoffeeMachineStatus.IDLE
        ),
        CoffeeMachine(
            _serial_number="CM-003",
            waiting_time=20,
            create_at=0,
            capacity=100.0,
            status=CoffeeMachineStatus.HIBERNATION,
        ),
    ]
    for m in demo_machines:
        cm_repo.save(m)

    cm_svc = CoffeeMachineService(cm_repo)
    order_svc = OrderService(order_repo)

    cm_vm = CoffeeMachineViewModel(cm_svc, order_svc)
    order_vm = OrderViewModel(order_svc)

    cm_view = CoffeeMachineView(cm_vm, terminal_enter, terminal_output)
    order_view = OrderView(order_vm, terminal_enter, terminal_output)

    print("☕ 欢迎来到咖啡店管理系统！")
    print("=" * 40)

    while True:
        print("\n=== 主菜单 ===")
        print("  [1] ☕ 制作咖啡")
        print("  [2] 📋 查看订单")
        print("  [3] 🌱 添加咖啡豆")
        print("  [4] 🔛 开机")
        print("  [5] 🔌 休眠")
        print("  [6] 🧹 清理咖啡机")
        print("  [7] ✅ 完成订单")
        print("  [0] 🚪 退出")

        choice = terminal_enter("请选择操作: ").strip()

        if choice == "1":
            cm_view.make_coffee()
            await asyncio.sleep(0.1)
        elif choice == "2":
            order_view.list_orders()
        elif choice == "3":
            cm_view.add_coffee_beans()
        elif choice == "4":
            cm_view.turn_on()
        elif choice == "5":
            cm_view.turn_off()
        elif choice == "6":
            cm_view.clean()
        elif choice == "7":
            order_view.finish()
        elif choice == "0":
            print("👋 感谢使用，再见！")
            break
        else:
            print("❌ 无效选项，请重新输入！")


if __name__ == "__main__":
    asyncio.run(main())
