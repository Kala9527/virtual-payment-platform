from app.models.order import PaymentMethod
from app.schemas.order import PaymentInstruction


class PaymentInstructionService:
    def get_instruction(self, method: PaymentMethod) -> PaymentInstruction:
        instructions = {
            PaymentMethod.alipay: PaymentInstruction(
                method=PaymentMethod.alipay,
                label="支付宝",
                qr_code_url="/assets/qrcodes/alipay-placeholder.svg",
                account_hint="扫码后请在备注中填写订单号",
            ),
            PaymentMethod.wechat: PaymentInstruction(
                method=PaymentMethod.wechat,
                label="微信支付",
                qr_code_url="/assets/qrcodes/wechat-placeholder.svg",
                account_hint="扫码后请在备注中填写订单号",
            ),
        }
        return instructions[method]

