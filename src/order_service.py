from typing import List
from src.entities import Order, OrderItem


class OrderService:
    def __init__(self):
        self.threshold_discount_config = None
        self.bogo_cosmetics_active = False
        self.double_11_active = False
        self.bulk_discount_config = None

    def set_threshold_discount(self, threshold: float, discount: float):
        """Configure threshold discount promotion"""
        self.threshold_discount_config = {
            'threshold': threshold,
            'discount': discount
        }

    def set_buy_one_get_one_for_cosmetics(self):
        """Activate buy one get one promotion for cosmetics"""
        self.bogo_cosmetics_active = True

    def set_double_11_active(self):
        """Activate Double 11 promotion"""
        self.double_11_active = True

    def set_bulk_discount_rule(self, group_size: int, discount_rate: float):
        """Configure bulk discount rule for Double 11"""
        self.bulk_discount_config = {
            'group_size': group_size,
            'discount_rate': discount_rate
        }

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

    def _calculate_bulk_discount(self, items: List[OrderItem]) -> float:
        """Calculate bulk discount for Double 11 promotion

        For each product, apply discount based on complete groups of group_size
        """
        if not self.double_11_active or not self.bulk_discount_config:
            return 0.0

        total_discount = 0.0
        group_size = self.bulk_discount_config['group_size']
        discount_rate = self.bulk_discount_config['discount_rate']

        for item in items:
            quantity = item.quantity
            # Calculate number of complete groups
            num_groups = quantity // group_size
            # Calculate discount for complete groups
            group_discount = num_groups * group_size * item.product.unit_price * discount_rate
            total_discount += group_discount

        return total_discount

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

        # Calculate discounts (can stack multiple discounts)
        threshold_discount = self._calculate_discount(subtotal)
        bulk_discount = self._calculate_bulk_discount(items)
        total_discount = threshold_discount + bulk_discount

        order.original_amount = subtotal
        order.discount = total_discount
        order.total_amount = subtotal - total_discount

        return order
