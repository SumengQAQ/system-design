from adapters.model import CoffeeMachine, Order
from adapters.exception import CoffeeMachineNotFoundError, OrderNotFoundError
from adapters.ports import CoffeeMachineRepository, OrderRepository


class MemoryCoffeeMachineRepository(CoffeeMachineRepository):
    def __init__(self):
        self._storage: list[CoffeeMachine] = []

    def save(self, coffee_machine: CoffeeMachine) -> bool:
        for i, cm in enumerate(self._storage):
            if cm._serial_number == coffee_machine._serial_number:
                self._storage[i] = coffee_machine
                return True
        self._storage.append(coffee_machine)
        return True

    def delete(self, coffee_machine: CoffeeMachine) -> bool:
        if not self._exists(coffee_machine._serial_number):
            raise CoffeeMachineNotFoundError(coffee_machine._serial_number, -1)
        self._storage = [cm for cm in self._storage if cm._serial_number != coffee_machine._serial_number]
        return True

    def get_all(self) -> list[CoffeeMachine]:
        return self._storage.copy()

    def get_one(self, serial_number: str) -> CoffeeMachine | None:
        for cm in self._storage:
            if cm._serial_number == serial_number:
                return cm
        return None

    def _exists(self, serial_number: str) -> bool:
        return any(cm._serial_number == serial_number for cm in self._storage)


class MemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._storage: list[Order] = []
        self._next_id: int = 1

    def save(self, order: Order) -> bool:
        if order.id is not None:
            for i, o in enumerate(self._storage):
                if o.id == order.id:
                    self._storage[i] = order
                    return True
        if order.id is None:
            order.id = self._next_id
            self._next_id += 1
        self._storage.append(order)
        return True

    def delete(self, order: Order) -> bool:
        order_id = order.id
        if order_id is None:
            raise OrderNotFoundError(0)
        if not self._exists(order_id):
            raise OrderNotFoundError(order_id)
        self._storage = [o for o in self._storage if o.id != order_id]
        return True

    def get_all(self) -> list[Order]:
        return self._storage.copy()

    def get_one(self, id: int) -> Order | None:
        for o in self._storage:
            if o.id == id:
                return o
        return None

    def _exists(self, id: int) -> bool:
        return any(o.id == id for o in self._storage)
