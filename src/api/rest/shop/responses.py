from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str


class CartItemResponse(BaseModel):
    product_id: int
    price: float
    pcs: int


class DeliveryAddressResponse(BaseModel):
    city: str
    street: str
    house: str
    apartment: int


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse] = []
    delivery_address: DeliveryAddressResponse | None = None


# "Богатый" ответ для GET /carts/{id} — включает имя и описание каждого товара,
# а также итоговую сумму. Это отдельный формат, заточенный под конкретную вьюху.
class RichCartItemResponse(BaseModel):
    product_id: int
    name: str
    price: float
    description: str
    pcs: int
    cost: float


class ShowCartResponse(BaseModel):
    id: int
    items: list[RichCartItemResponse] = []
    total_amount: float
    delivery_address: DeliveryAddressResponse | None = None
