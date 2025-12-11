from typing import List
from src.entities import Order, OrderItem


class OrderService:
    def __init__(self):
        self.threshold_discount_config = None
        self.bogo_cosmetics_active = False

    def set_threshold_discount(self, threshold: float, discount: float):
        """Configure threshold discount promotion"""
        self.threshold_discount_config = {
            'threshold': threshold,
            'discount': discount
        }

    def set_buy_one_get_one_for_cosmetics(self):
        """Activate buy one get one promotion for cosmetics"""
        self.bogo_cosmetics_active = True

    def _apply_bogo_cosmetics(self, items: List[OrderItem]) -> List[OrderItem]:
        """Apply buy-one-get-one promotion for cosmetics items

        For each cosmetic product, add 1 bonus unit regardless of quantity purchased
        """
        processed_items = []
        for item in items:
            if item.product.category == 'cosmetics':
                # Add 1 bonus unit for each cosmetic product
                new_item = OrderItem(product=item.product, quantity=item.quantity + 1)
                processed_items.append(new_item)
            else:
                processed_items.append(item)
        return processed_items

    def _calculate_subtotal(self, items: List[OrderItem]) -> float:
        """Calculate subtotal based on original item quantities"""
        subtotal = 0.0
        for item in items:
            subtotal += item.product.unit_price * item.quantity
        return subtotal

    def _calculate_discount(self, subtotal: float) -> float:
        """Calculate discount based on threshold promotion"""
        if self.threshold_discount_config and subtotal >= self.threshold_discount_config['threshold']:
            return self.threshold_discount_config['discount']
        return 0.0

    def checkout(self, items: List[OrderItem]) -> Order:
        """Build order and calculate order's total amount based on the discount offers"""
        order = Order()

        # Apply buy-one-get-one for cosmetics if active
        if self.bogo_cosmetics_active:
            order.items = self._apply_bogo_cosmetics(items)
        else:
            order.items = items

        # Calculate amounts
        subtotal = self._calculate_subtotal(items)
        discount = self._calculate_discount(subtotal)

        order.original_amount = subtotal
        order.discount = discount
        order.total_amount = subtotal - discount

        return order
