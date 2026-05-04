from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class CoffeeMachineStatus(Enum):
    """
    咖啡机

    Attributes:
        IDLE: 空闲
        HIBERNATION: 睡眠
        WORKING: 工作
        FAULT: 故障
    """

    IDLE = 0
    HIBERNATION = 1
    WORKING = 2
    FAULT = 3


class OrderStatus(Enum):
    """
    订单

    Attributes:
        TO_BE_PRODUCTED: 待制作
        IN_PRODUCTION: 制作中
        AWAITING_PICKUP: 待取餐
        COMPLETED: 已完成
        CANCELLED: 已取消
    """

    TO_BE_PRODUCTED = 0
    IN_PRODUCTION = 1
    AWAITING_PICKUP = 2
    COMPLETED = 3
    CANCELLED = 4


class CoffeeTypes(Enum):
    """
    咖啡种类

    Attributes:
        AMERICANO: 美式咖啡
        LATTE: 拿铁咖啡
        FLAT_WHITE: 白咖啡
        CAPPUCCINO: 卡布奇诺
    """

    AMERICANO = 0
    LATTE = 1
    FLAT_WHITE = 2
    CAPPUCCINO = 3


@dataclass(slots=True)
class CoffeeMachine:
    """
    咖啡机

    Attributes:
        _serial_number: 序列号
        waiting_time: 制作时间
        create_at: 制作开始时间
        consecutive_count: 连续制作次数
        capacity: 咖啡机容量
        status: 咖啡机状态
    """

    _serial_number: str
    waiting_time: int
    create_at: int
    consecutive_count: int = 0
    capacity: float = 0.0
    status: CoffeeMachineStatus = CoffeeMachineStatus.HIBERNATION

    def __str__(self):

        return "\n".join(
            f"{key}: {getattr(self, key)}"
            for key in ("_serial_number", "waiting_time", "create_at", "consecutive_count", "capacity", "status")
        )


@dataclass(slots=True)
class Order:
    """
    订单

    Attributes:
        customer_name: 用户名
        coffee_type: 咖啡种类
        create_at: 订单创建时间
        status: 订单状态
        id: 订单号
    """

    customer_name: str
    coffee_type: CoffeeTypes
    create_at: datetime = field(default_factory=datetime.now)
    status: OrderStatus = OrderStatus.TO_BE_PRODUCTED
    id: int | None = None

    def __str__(self):
        return "\n".join(
            f"{key}: {getattr(self, key)}" for key in ("id", "customer_name", "coffee_type", "create_at", "status")
        )
