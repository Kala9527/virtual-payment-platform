import argparse
from datetime import datetime
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session, joinedload  # noqa: E402

from app.db.init_db import init_db  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.models.order import Order  # noqa: E402
from app.models.product import Product, ProductSaleStatus  # noqa: E402


SALE_STATUS_LABELS = {
    ProductSaleStatus.on_sale.value: "在售",
    ProductSaleStatus.restocking.value: "补货中",
    ProductSaleStatus.discontinued.value: "停止发售",
}


def format_time(value: datetime | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%Y-%m-%d %H:%M:%S")


def print_table(headers: list[str], rows: list[list[object]]) -> None:
    values = [[str(item) for item in row] for row in rows]
    widths = [
        max(len(header), *(len(row[index]) for row in values)) if values else len(header)
        for index, header in enumerate(headers)
    ]
    print(" | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))
    for row in values:
        print(" | ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))


def list_products() -> None:
    init_db()
    with Session(engine) as db:
        products = db.query(Product).order_by(Product.id).all()

    print_table(
        ["ID", "商品名", "价格(分)", "状态", "通知邮箱"],
        [
            [
                product.id,
                product.name,
                product.price_cents,
                SALE_STATUS_LABELS.get(product.sale_status, product.sale_status),
                product.notification_email,
            ]
            for product in products
        ],
    )


def set_product_status(product_id: int, sale_status: int) -> None:
    if sale_status not in SALE_STATUS_LABELS:
        raise SystemExit("状态只能是 1、2、3。1=在售，2=补货中，3=停止发售")

    init_db()
    with Session(engine) as db:
        product = db.get(Product, product_id)
        if product is None:
            raise SystemExit(f"未找到商品 ID：{product_id}")

        product.sale_status = sale_status
        db.commit()
        print(f"已更新：{product.name} -> {SALE_STATUS_LABELS[sale_status]}")


def list_orders(limit: int) -> None:
    init_db()
    with Session(engine) as db:
        orders = (
            db.query(Order)
            .options(joinedload(Order.product))
            .order_by(Order.created_at.desc())
            .limit(limit)
            .all()
        )

    print_table(
        ["订单号", "商品", "状态", "支付方式", "备注", "下单时间", "支付时间"],
        [
            [
                order.order_no,
                order.product.name if order.product else "-",
                order.status,
                order.payment_method,
                order.remark or "",
                format_time(order.created_at),
                format_time(order.paid_confirmed_at),
            ]
            for order in orders
        ],
    )


def show_order(order_no: str) -> None:
    init_db()
    with Session(engine) as db:
        order = (
            db.query(Order)
            .options(joinedload(Order.product))
            .filter(Order.order_no == order_no)
            .one_or_none()
        )

    if order is None:
        raise SystemExit(f"未找到订单：{order_no}")

    rows = [
        ["订单号", order.order_no],
        ["商品", order.product.name if order.product else "-"],
        ["状态", order.status],
        ["支付方式", order.payment_method],
        ["金额(分)", order.amount_cents],
        ["币种", order.currency],
        ["买家邮箱", order.buyer_email or ""],
        ["备注", order.remark or ""],
        ["下单时间", format_time(order.created_at)],
        ["支付时间", format_time(order.paid_confirmed_at)],
    ]
    print_table(["字段", "值"], rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VirtualPay 后台管理脚本")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-products", help="查看商品列表和销售状态")

    status_parser = subparsers.add_parser("set-product-status", help="修改商品销售状态")
    status_parser.add_argument("product_id", type=int, help="商品 ID")
    status_parser.add_argument(
        "sale_status",
        type=int,
        choices=sorted(SALE_STATUS_LABELS),
        help="1=在售，2=补货中，3=停止发售",
    )

    orders_parser = subparsers.add_parser("list-orders", help="查看最近订单")
    orders_parser.add_argument("--limit", type=int, default=20, help="返回订单数量")

    order_parser = subparsers.add_parser("show-order", help="查看指定订单详情")
    order_parser.add_argument("order_no", help="订单号")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list-products":
        list_products()
    elif args.command == "set-product-status":
        set_product_status(args.product_id, args.sale_status)
    elif args.command == "list-orders":
        list_orders(args.limit)
    elif args.command == "show-order":
        show_order(args.order_no)


if __name__ == "__main__":
    main()
