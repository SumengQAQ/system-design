import pytest
from adapters.model import CoffeeMachine, Order, CoffeeTypes  # type:ignore
from adapters.exception import CoffeeMachineNotFoundError, OrderNotFoundError  # type:ignore


class TestMemoryCoffeeMachineRepository:
    def test_save_and_get_all(self, cm_repo):
        cm = CoffeeMachine(_serial_number="SN-TEST", waiting_time=10, create_at=0, capacity=100.0)
        cm_repo.save(cm)
        assert len(cm_repo.get_all()) == 1
        assert cm_repo.get_all()[0]._serial_number == "SN-TEST"

    def test_save_duplicate_upsert(self, cm_repo):
        cm = CoffeeMachine(_serial_number="SN-001", waiting_time=10, create_at=0, capacity=100.0)
        cm_repo.save(cm)
        cm.capacity = 200.0
        cm_repo.save(cm)
        assert len(cm_repo.get_all()) == 1
        assert cm_repo.get_all()[0].capacity == 200.0

    def test_get_one(self, cm_repo):
        cm = CoffeeMachine(_serial_number="SN-001", waiting_time=10, create_at=0, capacity=100.0)
        cm_repo.save(cm)
        found = cm_repo.get_one("SN-001")
        assert found is not None
        assert found._serial_number == "SN-001"

    def test_get_one_not_found(self, cm_repo):
        assert cm_repo.get_one("NOT-EXIST") is None

    def test_delete(self, cm_repo):
        cm = CoffeeMachine(_serial_number="SN-001", waiting_time=10, create_at=0, capacity=100.0)
        cm_repo.save(cm)
        cm_repo.delete(cm)
        assert len(cm_repo.get_all()) == 0

    def test_delete_not_found(self, cm_repo):
        cm = CoffeeMachine(_serial_number="SN-X", waiting_time=10, create_at=0, capacity=100.0)
        with pytest.raises(CoffeeMachineNotFoundError):
            cm_repo.delete(cm)

    def test_exists(self, cm_repo):
        cm = CoffeeMachine(_serial_number="SN-001", waiting_time=10, create_at=0, capacity=100.0)
        cm_repo.save(cm)
        assert cm_repo._exists("SN-001") is True
        assert cm_repo._exists("SN-XXX") is False

    def test_get_all_returns_copy(self, cm_repo):
        cm = CoffeeMachine(_serial_number="SN-001", waiting_time=10, create_at=0, capacity=100.0)
        cm_repo.save(cm)
        result = cm_repo.get_all()
        result.clear()
        assert len(cm_repo.get_all()) == 1


class TestMemoryOrderRepository:
    def test_save_auto_increment_id(self, order_repo):
        o1 = Order(customer_name="A", coffee_type=CoffeeTypes.LATTE)
        o2 = Order(customer_name="B", coffee_type=CoffeeTypes.AMERICANO)
        order_repo.save(o1)
        order_repo.save(o2)
        assert o1.id == 1
        assert o2.id == 2

    def test_get_all(self, order_repo):
        order_repo.save(Order(customer_name="A", coffee_type=CoffeeTypes.LATTE))
        assert len(order_repo.get_all()) == 1

    def test_get_one(self, order_repo):
        o = Order(customer_name="A", coffee_type=CoffeeTypes.LATTE)
        order_repo.save(o)
        found = order_repo.get_one(o.id)
        assert found is not None
        assert found.customer_name == "A"

    def test_get_one_not_found(self, order_repo):
        assert order_repo.get_one(999) is None

    def test_delete(self, order_repo):
        o = Order(customer_name="A", coffee_type=CoffeeTypes.LATTE)
        order_repo.save(o)
        order_repo.delete(o)
        assert len(order_repo.get_all()) == 0

    def test_delete_not_found(self, order_repo):
        o = Order(customer_name="A", coffee_type=CoffeeTypes.LATTE, id=999)
        with pytest.raises(OrderNotFoundError):
            order_repo.delete(o)

    def test_upsert(self, order_repo):
        o = Order(customer_name="A", coffee_type=CoffeeTypes.LATTE)
        order_repo.save(o)
        o.customer_name = "B"
        order_repo.save(o)
        assert len(order_repo.get_all()) == 1
        assert order_repo.get_one(o.id).customer_name == "B"
