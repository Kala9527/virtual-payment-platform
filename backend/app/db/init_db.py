from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.models.product import Product, ProductSaleStatus


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    migrate_existing_schema()
    with Session(engine) as db:
        seed_products(db)


def migrate_existing_schema() -> None:
    inspector = inspect(engine)
    if "products" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("products")}
    if "sale_status" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE products "
                    f"ADD COLUMN sale_status INTEGER NOT NULL DEFAULT {ProductSaleStatus.on_sale.value}"
                )
            )


def seed_products(db: Session) -> None:
    existing = db.scalar(select(Product).limit(1))
    if existing:
        return

    settings = get_settings()
    products = [
        Product(
            name="独立游戏数字激活包",
            slug="indie-game-pack",
            category="游戏",
            summary="适合轻量玩家的数字激活与入门资料包。",
            description="包含虚拟游戏激活说明、安装指南和基础玩法资料。付款确认后由商家按邮箱交付。",
            price_cents=990,
            currency="CNY",
            image_url="/assets/products/game-placeholder.svg",
            delivery_hint="确认收款后通过邮箱发送激活信息。",
            notification_email=str(settings.merchant_email),
            sale_status=ProductSaleStatus.on_sale.value,
        ),
        Product(
            name="在线服务月度订阅",
            slug="online-service-monthly",
            category="在线服务",
            summary="适合个人使用的在线服务月度访问权益。",
            description="提供一个月的在线服务使用权益。请在备注中填写期望开通账号或联系方式。",
            price_cents=2990,
            currency="CNY",
            image_url="/assets/products/service-placeholder.svg",
            delivery_hint="确认收款后开通服务并发送访问说明。",
            notification_email=str(settings.merchant_email),
            sale_status=ProductSaleStatus.restocking.value,
        ),
        Product(
            name="数字内容高级资源包",
            slug="digital-resource-pro",
            category="数字内容",
            summary="面向创作者和开发者的虚拟资源组合。",
            description="包含可下载的数字资源、使用说明和更新入口。付款确认后发送资源访问链接。",
            price_cents=5990,
            currency="CNY",
            image_url="/assets/products/resource-placeholder.svg",
            delivery_hint="确认收款后发送资源链接和授权说明。",
            notification_email=str(settings.merchant_email),
            sale_status=ProductSaleStatus.discontinued.value,
        ),
    ]
    db.add_all(products)
    db.commit()
