from support.models import Order


def get_order(order_id: int) -> Order | None:
    return (
        Order.objects.select_related("customer")
        .prefetch_related("items__product")
        .filter(id=order_id)
        .first()
    )


def get_customer_orders(customer_id: int, limit: int = 5) -> list[Order]:
    return list(
        Order.objects.filter(customer_id=customer_id)
        .select_related("customer")
        .prefetch_related("items__product")[:limit]
    )

