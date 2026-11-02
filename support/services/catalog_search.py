from django.db.models import Count, Prefetch, Q

from support.models import Product, Promotion


def get_catalog_summary() -> list[dict[str, int | str]]:
    rows = list(
        Product.objects.filter(status="active", stock_quantity__gt=0)
        .values("category__name")
        .annotate(product_count=Count("id"))
        .order_by("category__name")
    )
    return [
        {
            "category_name": row["category__name"],
            "product_count": row["product_count"],
        }
        for row in rows
    ]


def get_active_promotions() -> list[Promotion]:
    return list(
        Promotion.objects.filter(
            is_active=True,
            product__status="active",
            product__stock_quantity__gt=0,
        )
        .select_related("product", "product__category")
        .order_by("product__name")
    )


def search_products(
    query: str = "",
    max_price: float | None = None,
    limit: int | None = 5,
    order_by_price: bool = False,
    category_name: str = "",
) -> list[Product]:
    products = Product.objects.filter(status="active", stock_quantity__gt=0)
    if category_name:
        products = products.filter(category__name=category_name)
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
        )
    if max_price is not None:
        products = products.filter(price_brl__lte=max_price)
    products = products.select_related("category").prefetch_related(
        Prefetch(
            "promotions",
            queryset=Promotion.objects.filter(is_active=True),
            to_attr="active_promotions",
        )
    )
    if order_by_price:
        products = products.order_by("price_brl", "name")
    return list(products if limit is None else products[:limit])

