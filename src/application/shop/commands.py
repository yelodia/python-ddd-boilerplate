from pydantic import BaseModel


class ShowAllProductsCmd(BaseModel):
    offset: int = 0
    limit: int = 20


class CreateProductCmd(BaseModel):
    name: str
    price: float
    description: str


class UpdateProductCmd(BaseModel):
    product_id: int
    name: str
    price: float
    description: str


class ShowAllCartsCmd(BaseModel):
    offset: int = 0
    limit: int = 20


class CreateEmptyCartCmd(BaseModel):
    pass


class ShowCartCmd(BaseModel):
    cart_id: int


class PutProductToCartCmd(BaseModel):
    cart_id: int
    product_id: int
    pcs: int


class RemoveProductFromCartCmd(BaseModel):
    cart_id: int
    product_id: int


class UpdateCartDeliveryAddressCmd(BaseModel):
    cart_id: int
    city: str
    street: str
    house: str
    apartment: int


class ClearCartCmd(BaseModel):
    cart_id: int


class RemoveCart(BaseModel):
    cart_id: int
