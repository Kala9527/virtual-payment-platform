from pydantic import BaseModel, ConfigDict


class ProductRead(BaseModel):
    id: int
    name: str
    slug: str
    category: str
    summary: str
    description: str
    price_cents: int
    currency: str
    image_url: str
    delivery_hint: str
    sale_status: int

    model_config = ConfigDict(from_attributes=True)
