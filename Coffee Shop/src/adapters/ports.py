from abc import ABC, abstractmethod

from adapters.model import CoffeeMachine, Order


class CoffeeMachineRepository(ABC):
    """咖啡机数据库操作"""

    @abstractmethod
    def save(self, coffee_machine: CoffeeMachine) -> bool:
        """
        将咖啡机保存至内存中
        Args:
            coffee_machine (CoffeeMachine): 咖啡机

        Returns:
            是否成功
        """
        ...

    @abstractmethod
    def delete(self, coffee_machine: CoffeeMachine) -> bool:
        """
        删除咖啡机

        Args:
            coffee_machine (CoffeeMachine): 咖啡机

        Returns:
            是否成功
        """
        ...

    @abstractmethod
    def get_all(self) -> list[CoffeeMachine]:
        """
        获取全部的咖啡机

        Returns:
            咖啡机列表
        """
        ...

    @abstractmethod
    def get_one(self, serial_number: str) -> CoffeeMachine | None:
        """
        获取指定的咖啡机

        Args:
            serial_number (str): 咖啡机序列号

        Returns:
            咖啡机
        """
        ...

    @abstractmethod
    def _exists(self, serial_number: str) -> bool:
        """
        判断咖啡机是否存在

        Args:
            serial_number (str): 咖啡机序列号

        Returns:
            是否存在
        """
        ...


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> bool:
        """
        保存订单

        Args:
            order (Order): 订单

        Returns:
            是否成功
        """
        ...

    @abstractmethod
    def delete(self, order: Order) -> bool:
        """
        删除订单

        Args:
            order (Order): 订单

        Returns:
            是否成功
        """
        ...

    @abstractmethod
    def get_all(self) -> list[Order]:
        """
        获取全部的订单

        Returns:
            订单列表
        """
        ...

    @abstractmethod
    def get_one(self, id: int) -> Order | None:
        """
        获取指定的订单

        Args:
            id (int): 订单ID

        Returns:
            订单
        """
        ...

    @abstractmethod
    def _exists(self, id: int) -> bool:
        """
        判断订单是否存在

        Args:
            id (int): 订单ID

        Returns:
            是否存在
        """
        ...
