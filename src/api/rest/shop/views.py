from dataclasses import asdict

from fastapi import APIRouter
from starlette import status

from api.dependencies import build
from api.rest.shop.responses import (
    ProductResponse,
    CartResponse,
    ShowCartResponse,
    RichCartItemResponse,
    DeliveryAddressResponse,
)
from application.shop.commands import (
    ShowAllProductsCmd,
    CreateProductCmd,
    CreateEmptyCartCmd,
    PutProductToCartCmd,
    ShowCartCmd,
    ClearCartCmd,
    RemoveProductFromCartCmd,
)
from application.shop.use_cases import (
    ShowAllProductsUseCase,
    CreateProductUseCase,
    CreateEmptyCartUseCase,
    PutProductToCartUseCase,
    ShowCartUseCase,
    ClearCartUseCase,
    RemoveProductFromCartUseCase,
)

products_router = APIRouter(prefix="/products", tags=["products"])
carts_router = APIRouter(prefix="/carts", tags=["carts"])


# region Product Views
@products_router.get("/", response_model=list[ProductResponse])
async def show_all_products_view(
        offset: int = 0,
        limit: int = 20,
        use_case: ShowAllProductsUseCase = build(ShowAllProductsUseCase),
) -> list[ProductResponse]:
    cmd = ShowAllProductsCmd(offset=offset, limit=limit)
    products = await use_case.execute(cmd)
    return [ProductResponse.model_validate(asdict(x)) for x in products]


@products_router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
        cmd: CreateProductCmd,
        use_case: CreateProductUseCase = build(CreateProductUseCase),
) -> ProductResponse:
    product = await use_case.execute(cmd)
    return ProductResponse.model_validate(asdict(product))


# endregion
# region Cart Views
@carts_router.post("/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_empty_cart(
        use_case: CreateEmptyCartUseCase = build(CreateEmptyCartUseCase)
) -> CartResponse:
    cmd = CreateEmptyCartCmd()
    new_cart = await use_case.execute(cmd)
    return CartResponse.model_validate(asdict(new_cart))


@carts_router.post("/{cart_id}", response_model=CartResponse)
async def put_product_to_cart(
        cart_id: int,
        product_id: int,
        pcs: int,
        use_case: PutProductToCartUseCase = build(PutProductToCartUseCase),
) -> CartResponse:
    cmd = PutProductToCartCmd(cart_id=cart_id, product_id=product_id, pcs=pcs)
    updated_cart = await use_case.execute(cmd)
    return CartResponse.model_validate(asdict(updated_cart))


@carts_router.get("/{cart_id}", response_model=ShowCartResponse)
async def get_cart(
        cart_id: int,
        use_case: ShowCartUseCase = build(ShowCartUseCase),
) -> ShowCartResponse:
    cmd = ShowCartCmd(cart_id=cart_id)
    cart, products = await use_case.execute(cmd)

    products_by_id = {p.id: p for p in products}
    rich_items = [
        RichCartItemResponse(
            product_id=item.product_id,
            name=products_by_id[item.product_id].name,
            price=item.price,
            description=products_by_id[item.product_id].description,
            pcs=item.pcs,
            cost=item.cost,
        )
        for item in cart.items
    ]

    return ShowCartResponse(
        id=cart.id,
        items=rich_items,
        total_amount=cart.total_amount,
        delivery_address=DeliveryAddressResponse.model_validate(asdict(cart.delivery_address))
        if cart.delivery_address else None,
    )


@carts_router.delete("/{cart_id}/{product_id}", response_model=CartResponse)
async def remove_product_from_cart(
        cart_id: int,
        product_id: int,
        use_case: RemoveProductFromCartUseCase = build(RemoveProductFromCartUseCase),
) -> CartResponse:
    cmd = RemoveProductFromCartCmd(cart_id=cart_id, product_id=product_id)
    updated_cart = await use_case.execute(cmd)
    return CartResponse.model_validate(asdict(updated_cart))


@carts_router.delete("/{cart_id}", response_model=CartResponse)
async def clear_cart(
        cart_id: int,
        use_case: ClearCartUseCase = build(ClearCartUseCase),
) -> CartResponse:
    cmd = ClearCartCmd(cart_id=cart_id)
    cart = await use_case.execute(cmd)
    return CartResponse.model_validate(asdict(cart))

# endregion
