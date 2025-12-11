from dataclasses import dataclass
from typing import List


@dataclass
class Product:
    name: str
    unit_price: float
    category: str = ""


@dataclass
class OrderItem:
    product: Product
    quantity: int


@dataclass
class Order:
    total_amount: float = 0.0
    original_amount: float = 0.0
    discount: float = 0.0
    items: List[OrderItem] = None

    def __post_init__(self):
        if self.items is None:
            self.items = []
