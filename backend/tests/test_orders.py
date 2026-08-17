from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import engine
from app.main import app
from app.models.order import Order
from app.models.product import Product
from app.services.order_service import OrderService


def test_create_and_confirm_order_with_required_email():
    with TestClient(app) as client:
        products = client.get("/api/products").json()
        assert products
        assert "sale_status" in products[0]

        created = client.post(
            "/api/orders",
            json={
                "product_id": products[0]["id"],
                "buyer_email": "buyer@example.com",
                "payment_method": "alipay",
                "remark": "测试订单",
            },
        )
        assert created.status_code == 201
        order = created.json()
        assert order["status"] == "pending"
        assert order["buyer_email"] == "buyer@example.com"
        assert order["payment_instruction"]["qr_code_url"].endswith("alipay-placeholder.svg")

        confirmed = client.post(f"/api/orders/{order['order_no']}/confirm")
        assert confirmed.status_code == 200
        body = confirmed.json()
        assert body["order"]["status"] == "paid_confirmed"
        assert body["notification_sent"] is True


def test_rejects_invalid_email():
    with TestClient(app) as client:
        products = client.get("/api/products").json()

        response = client.post(
            "/api/orders",
            json={
                "product_id": products[0]["id"],
                "buyer_email": "not-an-email",
                "payment_method": "wechat",
                "remark": "",
            },
        )

        assert response.status_code == 422


def test_rejects_missing_email():
    with TestClient(app) as client:
        products = client.get("/api/products").json()

        response = client.post(
            "/api/orders",
            json={
                "product_id": products[0]["id"],
                "buyer_email": "",
                "payment_method": "wechat",
                "remark": "",
            },
        )

        assert response.status_code == 422


def test_cannot_create_order_for_unavailable_product():
    with TestClient(app) as client:
        products = client.get("/api/products").json()
        product = products[0]

        with Session(engine) as db:
            db_product = db.get(Product, product["id"])
            original_status = db_product.sale_status
            db_product.sale_status = 2
            db.commit()

        response = client.post(
            "/api/orders",
            json={
                "product_id": product["id"],
                "buyer_email": "buyer@example.com",
                "payment_method": "alipay",
                "remark": "应该被拒绝",
            },
        )

        with Session(engine) as db:
            db_product = db.get(Product, product["id"])
            db_product.sale_status = original_status
            db.commit()

        assert response.status_code == 400
        assert response.json()["detail"] == "商品当前不可购买"


def test_order_notification_email_format():
    service = object.__new__(OrderService)
    order = Order(
        order_no="VP20260813ABCDEF1234",
        payment_method="wechat",
        buyer_email="buyer@example.com",
        remark="测试备注",
    )
    action_time = datetime(2026, 8, 13, 10, 30, 45)

    subject = service._build_notification_subject(order, "已支付")
    body = service._build_notification_body(order, "支付", action_time)

    assert subject == "VP20260813ABCDEF1234（已支付）"
    assert body == (
        "订单号：VP20260813ABCDEF1234\n"
        "支付时间：2026-08-13 10:30:45\n"
        "支付方式：微信支付\n"
        "联系方式：buyer@example.com\n"
        "备注:测试备注"
    )
