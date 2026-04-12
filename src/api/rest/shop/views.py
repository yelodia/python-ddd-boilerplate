from dataclasses import asdict

from fastapi import APIRouter
from starlette import status

from api.dependencies import build
from api.rest.shop.responses import ProductResponse, CartResponse
from application.shop.commands import (
    ShowAllProductsCmd,
    CreateProductCmd,
    CreateEmptyCartCmd,
    PutProductToCartCmd,
    ShowCartCmd,
)
from application.shop.use_cases import (
    ShowAllProductsUseCase,
    CreateProductUseCase,
    CreateEmptyCartUseCase,
    PutProductToCartUseCase,
    ShowCartUseCase,
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


@carts_router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(
        cart_id: int,
        use_case: ShowCartUseCase = build(ShowCartUseCase),
) -> CartResponse:
    cmd = ShowCartCmd(cart_id=cart_id)
    cart = await use_case.execute(cmd)
    return CartResponse.model_validate(asdict(cart))

# endregion
