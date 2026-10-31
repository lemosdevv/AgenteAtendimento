from django.db.models import Q

from support.models import Product


def search_products(
    query: str = "",
    max_price: float | None = None,
    limit: int = 5,
) -> list[Product]:
    products = Product.objects.filter(status="active", stock_quantity__gt=0)
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )
    if max_price is not None:
        products = products.filter(price_brl__lte=max_price)
    return list(products.select_related("category")[:limit])

