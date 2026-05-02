from adapters.ports import CoffeeMachineRepository, OrderRepository
from adapters.model import CoffeeMachine, Order, CoffeeTypes, CoffeeMachineStatus, OrderStatus
from adapters.exception import (
    CoffeeMachineFaultError,
    CoffeeMachineAlreadyWorkingError,
    CoffeeMachineNotTurnOn,
    CoffeeMachineNotFoundError,
    OrderNotFoundError,
    InsufficientCoffeeBeansError,
    CoffeeBeanOverflowError,
    CoffeeMachineAlreadyWorkingError,
)

COFFEE_BEANS_PER_CUP = 15.0
CLEAN_REMINDER_THRESHOLD = 5


class CoffeeMachineService:
    def __init__(self, coffee_machine_repository: CoffeeMachineRepository) -> None:
        self._repo = coffee_machine_repository
        machines = self._repo.get_all()
        if machines:
            self._coffee_machines = machines
        else:
            self._coffee_machines = []

    def make_coffee(self, coffee_machine_index: int, waiting_time: int) -> bool:
        self._validate_index(coffee_machine_index)
        cm = self._coffee_machines[coffee_machine_index]

        if cm.status == CoffeeMachineStatus.FAULT:
            raise CoffeeMachineFaultError(cm._serial_number, coffee_machine_index)
        if cm.status == CoffeeMachineStatus.WORKING:
            raise CoffeeMachineAlreadyWorkingError(cm._serial_number, coffee_machine_index)
        if cm.status == CoffeeMachineStatus.HIBERNATION:
            raise CoffeeMachineNotTurnOn(cm._serial_number, coffee_machine_index)
        if cm.capacity < COFFEE_BEANS_PER_CUP:
            raise InsufficientCoffeeBeansError(cm._serial_number, coffee_machine_index)

        cm.capacity -= COFFEE_BEANS_PER_CUP
        cm.status = CoffeeMachineStatus.WORKING
        cm.create_at = waiting_time
        self._repo.save(cm)
        return True

    def add_coffee_beans(self, coffee_machine_index: int, grams: float) -> int:
        self._validate_index(coffee_machine_index)
        cm = self._coffee_machines[coffee_machine_index]
        new_capacity = cm.capacity + grams
        if new_capacity > 500:
            raise CoffeeBeanOverflowError(cm._serial_number, coffee_machine_index)
        cm.capacity = new_capacity
        self._repo.save(cm)
        return int(cm.capacity)

    def cost_coffee_beans(self, coffee_machine_index: int, grams: float) -> int:
        self._validate_index(coffee_machine_index)
        cm = self._coffee_machines[coffee_machine_index]
        if cm.capacity < grams:
            raise InsufficientCoffeeBeansError(cm._serial_number, coffee_machine_index)
        cm.capacity -= grams
        self._repo.save(cm)
        return int(cm.capacity)

    def change_status(self, coffee_machine_index: int, coffee_machine_status: CoffeeMachineStatus) -> bool:
        self._validate_index(coffee_machine_index)
        cm = self._coffee_machines[coffee_machine_index]
        cm.status = coffee_machine_status
        self._repo.save(cm)
        return True

    def turn_off(self, coffee_machine_index: int) -> bool:
        self._validate_index(coffee_machine_index)
        cm = self._coffee_machines[coffee_machine_index]
        if cm.status == CoffeeMachineStatus.WORKING:
            raise CoffeeMachineAlreadyWorkingError(cm._serial_number, coffee_machine_index)
        cm.status = CoffeeMachineStatus.HIBERNATION
        self._repo.save(cm)
        return True

    def increace_consecutive_count(self, coffee_machine_index: int) -> int:
        self._validate_index(coffee_machine_index)
        cm = self._coffee_machines[coffee_machine_index]
        cm.consecutive_count += 1
        self._repo.save(cm)
        return cm.consecutive_count

    def clean(self, coffee_machine_index: int) -> bool:
        self._validate_index(coffee_machine_index)
        cm = self._coffee_machines[coffee_machine_index]
        cm.consecutive_count = 0
        self._repo.save(cm)
        return True

    def get_all(self) -> list[CoffeeMachine]:
        self._coffee_machines = self._repo.get_all()
        return self._coffee_machines

    def get_one(self, serial_number: str) -> CoffeeMachine | None:
        return self._repo.get_one(serial_number)

    def _validate_index(self, index: int) -> None:
        if index < 0 or index >= len(self._coffee_machines):
            raise CoffeeMachineNotFoundError("unknown", index)


class OrderService:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._repo = order_repository
        self._orders = self._repo.get_all()

    def create(self, user_name: str, coffee_types: CoffeeTypes) -> bool:
        order = Order(customer_name=user_name, coffee_type=coffee_types)
        return self._repo.save(order)

    def change_status(self, id: int, order_status: OrderStatus) -> bool:
        order = self._repo.get_one(id)
        if order is None:
            raise OrderNotFoundError(id)
        order.status = order_status
        self._repo.save(order)
        return True

    def get_all(self) -> list[Order]:
        self._orders = self._repo.get_all()
        return self._orders

    def get_one(self, id: int) -> Order | None:
        return self._repo.get_one(id)
