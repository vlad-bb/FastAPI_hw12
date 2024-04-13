from pydantic import BaseModel


class ShopData(BaseModel):
    products: list
    totalPrice: float
    # queryId: any  # todo when React will be ready to send user_id


class PaymentRequest(BaseModel):
    type: str
    data: dict


class PaymentResponse(BaseModel):
    ok: bool
