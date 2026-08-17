from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product, ProductSaleStatus


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Product]:
        statement = select(Product).order_by(Product.id)
        return list(self.db.scalars(statement).all())

    def get_orderable(self, product_id: int) -> Product | None:
        statement = select(Product).where(
            Product.id == product_id,
            Product.sale_status == ProductSaleStatus.on_sale.value,
        )
        return self.db.scalar(statement)

    def get_by_id(self, product_id: int) -> Product | None:
        statement = select(Product).where(Product.id == product_id)
        return self.db.scalar(statement)
