from application.use_case_base import Command


class ShowAllProductsCmd(Command):
    offset: int = 0
    limit: int = 20


class CreateProductCmd(Command):
    name: str
    price: float
    description: str


class UpdateProductCmd(Command):
    product_id: int
    name: str
    price: float
    description: str


class ShowAllCartsCmd(Command):
    offset: int = 0
    limit: int = 20


class CreateEmptyCartCmd(Command):
    pass


class ShowCartCmd(Command):
    cart_id: int


class PutProductToCartCmd(Command):
    cart_id: int
    product_id: int
    pcs: int


class RemoveProductFromCartCmd(Command):
    cart_id: int
    product_id: int


class UpdateCartDeliveryAddressCmd(Command):
    cart_id: int
    city: str
    street: str
    house: str
    apartment: int


class ClearCartCmd(Command):
    cart_id: int


class RemoveCart(Command):
    cart_id: int
