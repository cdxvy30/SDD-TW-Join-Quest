from behave import given, when, then
from src.entities import Product, OrderItem
from src.order_service import OrderService


@given('no promotions are applied')
def step_no_promotions(context):
    context.order_service = OrderService()


@given('the threshold discount promotion is configured:')
def step_configure_threshold_discount(context):
    # Create service if not exists, otherwise reuse
    if not hasattr(context, 'order_service'):
        context.order_service = OrderService()

    for row in context.table:
        threshold = float(row['threshold'])
        discount = float(row['discount'])
        context.order_service.set_threshold_discount(threshold, discount)


@given('the buy one get one promotion for cosmetics is active')
def step_configure_bogo_cosmetics(context):
    # Create service if not exists, otherwise reuse
    if not hasattr(context, 'order_service'):
        context.order_service = OrderService()

    context.order_service.set_buy_one_get_one_for_cosmetics()


@given('the Double 11 promotion is active')
def step_double_11_active(context):
    # Create service if not exists, otherwise reuse
    if not hasattr(context, 'order_service'):
        context.order_service = OrderService()

    context.order_service.set_double_11_active()


@given('the bulk discount rule for Double 11 is:')
def step_configure_bulk_discount(context):
    # Create service if not exists, otherwise reuse
    if not hasattr(context, 'order_service'):
        context.order_service = OrderService()

    for row in context.table:
        group_size = int(row['groupSize'])
        discount_rate_str = row['discountRate']
        # Parse percentage string (e.g., "20%" -> 0.20)
        discount_rate = float(discount_rate_str.rstrip('%')) / 100.0
        context.order_service.set_bulk_discount_rule(group_size, discount_rate)


@when('a customer places an order with:')
def step_place_order(context):
    items = []
    for row in context.table:
        product_name = row['productName']
        quantity = int(row['quantity'])
        unit_price = float(row['unitPrice'])
        category = row.get('category', '')

        product = Product(name=product_name, unit_price=unit_price, category=category)
        order_item = OrderItem(product=product, quantity=quantity)
        items.append(order_item)

    context.order = context.order_service.checkout(items)


@then('the order summary should be:')
def step_verify_order_summary(context):
    for row in context.table:
        if 'totalAmount' in row.headings:
            expected_total = float(row['totalAmount'])
            assert context.order.total_amount == expected_total, \
                f"Expected total_amount {expected_total}, got {context.order.total_amount}"

        if 'originalAmount' in row.headings:
            expected_original = float(row['originalAmount'])
            assert context.order.original_amount == expected_original, \
                f"Expected original_amount {expected_original}, got {context.order.original_amount}"

        if 'discount' in row.headings:
            expected_discount = float(row['discount'])
            assert context.order.discount == expected_discount, \
                f"Expected discount {expected_discount}, got {context.order.discount}"


@then('the customer should receive:')
def step_verify_items_received(context):
    for row in context.table:
        product_name = row['productName']
        expected_quantity = int(row['quantity'])

        # Find the matching item in the order
        found = False
        for order_item in context.order.items:
            if order_item.product.name == product_name:
                found = True
                assert order_item.quantity == expected_quantity, \
                    f"Expected {product_name} quantity {expected_quantity}, got {order_item.quantity}"
                break

        assert found, f"Product {product_name} not found in order"
