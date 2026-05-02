class OrderExistError(Exception):
    def __init__(self, order_id: int) -> None:
        self.order_id = order_id
        super().__init__(f"订单 #{order_id} 已存在")


class OrderNotFoundError(Exception):
    def __init__(self, order_id: int) -> None:
        self.order_id = order_id
        super().__init__(f"订单 #{order_id} 不存在")


class CoffeeMachineExistError(Exception):
    def __init__(self, serial_number: str, coffee_machine_index: int) -> None:
        self.serial_number = serial_number
        self.coffee_machine_index = coffee_machine_index
        super().__init__(f"咖啡机 [{serial_number}] (下标 {coffee_machine_index}) 已存在")


class CoffeeMachineNotFoundError(Exception):
    def __init__(self, serial_number: str, coffee_machine_index: int) -> None:
        self.serial_number = serial_number
        self.coffee_machine_index = coffee_machine_index
        super().__init__(f"咖啡机 [{serial_number}] (下标 {coffee_machine_index}) 不存在")


class CoffeeMachineFaultError(Exception):
    def __init__(self, serial_number: str, coffee_machine_index: int) -> None:
        self.serial_number = serial_number
        self.coffee_machine_index = coffee_machine_index
        super().__init__(f"咖啡机 [{serial_number}] (下标 {coffee_machine_index}) 故障中，无法操作")


class CoffeeMachineAlreadyWorkingError(Exception):
    def __init__(self, serial_number: str, coffee_machine_index: int) -> None:
        self.serial_number = serial_number
        self.coffee_machine_index = coffee_machine_index
        super().__init__(f"咖啡机 [{serial_number}] (下标 {coffee_machine_index}) 正在工作中")


class CoffeeMachineNotTurnOn(Exception):
    def __init__(self, serial_number: str, coffee_machine_index: int) -> None:
        self.serial_number = serial_number
        self.coffee_machine_index = coffee_machine_index
        super().__init__(f"咖啡机 [{serial_number}] (下标 {coffee_machine_index}) 未开机")


class InsufficientCoffeeBeansError(Exception):
    def __init__(self, serial_number: str, coffee_machine_index: int) -> None:
        self.serial_number = serial_number
        self.coffee_machine_index = coffee_machine_index
        super().__init__(f"咖啡机 [{serial_number}] (下标 {coffee_machine_index}) 咖啡豆不足")


class CoffeeBeanOverflowError(Exception):
    def __init__(self, serial_number: str, coffee_machine_index: int) -> None:
        self.serial_number = serial_number
        self.coffee_machine_index = coffee_machine_index
        super().__init__(f"咖啡机 [{serial_number}] (下标 {coffee_machine_index}) 咖啡豆添加过多")
