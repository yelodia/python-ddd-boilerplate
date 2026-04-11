from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse] = []
    delivery_address: DeliveryAddressResponse | None = None


class CartItemResponse(BaseModel):
    product_id: int
    price: float
    pcs: int


class DeliveryAddressResponse(BaseModel):
    city: str
    street: str
    house: str
    apartment: int
