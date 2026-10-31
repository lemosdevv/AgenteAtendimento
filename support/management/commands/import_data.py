import csv
import json
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from support.models import Category, Customer, Order, OrderItem, Product, Promotion


class Command(BaseCommand):
    help = "Import the supplied CSV files into the SQLite database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            default="data",
            help="Directory containing the challenge CSV files.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"]).resolve()
        if not data_dir.is_dir():
            raise CommandError(f"Data directory not found: {data_dir}")

        self._import_categories(data_dir)
        self._import_customers(data_dir)
        self._import_products(data_dir)
        self._import_orders(data_dir)
        self._import_order_items(data_dir)
        self._import_promotions(data_dir)

        self.stdout.write(self.style.SUCCESS("Data import completed successfully."))

    def _read_rows(self, data_dir: Path, filename: str):
        path = data_dir / filename
        if not path.is_file():
            raise CommandError(f"Required data file not found: {path}")
        with path.open(encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))

    def _import_categories(self, data_dir: Path):
        for row in self._read_rows(data_dir, "desafio_tecnico_ai_eng - categories.csv"):
            Category.objects.update_or_create(
                id=int(row["category_id"]),
                defaults={
                    "name": row["name"],
                    "description": row["description"],
                },
            )

    def _import_customers(self, data_dir: Path):
        for row in self._read_rows(data_dir, "desafio_tecnico_ai_eng - customers.csv"):
            Customer.objects.update_or_create(
                id=int(row["customer_id"]),
                defaults={
                    "name": row["name"],
                    "phone": row["phone"],
                    "email": row["email"],
                    "city": row["city"],
                },
            )

    def _import_products(self, data_dir: Path):
        for row in self._read_rows(data_dir, "desafio_tecnico_ai_eng - products.csv"):
            Product.objects.update_or_create(
                id=int(row["product_id"]),
                defaults={
                    "price_brl": row["price_brl"],
                    "name": row["name"],
                    "category_id": int(row["category_id"]),
                    "description": row["description"],
                    "stock_quantity": int(row["stock_quantity"]),
                    "status": row["status"],
                    "specs": json.loads(row["specs"]),
                    "created_at": date.fromisoformat(row["created_at"]),
                },
            )

    def _import_orders(self, data_dir: Path):
        for row in self._read_rows(data_dir, "desafio_tecnico_ai_eng - orders.csv"):
            estimated_delivery = row["estimated_delivery"] or None
            Order.objects.update_or_create(
                id=int(row["order_id"]),
                defaults={
                    "customer_id": int(row["customer_id"]),
                    "order_date": date.fromisoformat(row["order_date"]),
                    "status": row["status"],
                    "total_brl": row["total_brl"],
                    "payment_method": row["payment_method"],
                    "tracking_code": row["tracking_code"],
                    "estimated_delivery": (
                        date.fromisoformat(estimated_delivery)
                        if estimated_delivery
                        else None
                    ),
                    "notes": row["notes"],
                },
            )

    def _import_order_items(self, data_dir: Path):
        for row in self._read_rows(data_dir, "desafio_tecnico_ai_eng - order_items.csv"):
            OrderItem.objects.update_or_create(
                order_id=int(row["order_id"]),
                product_id=int(row["product_id"]),
                defaults={"quantity": int(row["quantity"])},
            )

    def _import_promotions(self, data_dir: Path):
        for row in self._read_rows(data_dir, "desafio_tecnico_ai_eng - promotions.csv"):
            Promotion.objects.update_or_create(
                id=int(row["promotion_id"]),
                defaults={
                    "product_id": int(row["product_id"]),
                    "discount_percent": row["discount_percent"],
                    "description": row["description"],
                    "is_active": row["is_active"] == "1",
                },
            )

