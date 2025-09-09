from fastapi import APIRouter, Depends, HTTPException, status, Request
from uuid import UUID
from .domain import ProductCreate, Product, ProductUpdate
from .repo import ProductRepository
from .errors import AlreadyExists, NotFound

def build_products_router(repo: ProductRepository) -> APIRouter:
    r = APIRouter(prefix="/products", tags=["products"])

    @r.post("", status_code=status.HTTP_201_CREATED)
    async def create_product(dto: ProductCreate):
        existing = await repo.get(dto.id)
        if existing:
            raise AlreadyExists()
        await repo.add(Product(**dto.model_dump()))
        return {}

    @r.get("", response_model=list[Product])
    async def list_products():
        return await repo.list()

    @r.get("/{id}", response_model=Product)
    async def get_product(id: UUID):
        p = await repo.get(id)
        if not p:
            raise NotFound()
        return p

    @r.patch("/{id}", response_model=Product)
    async def update_product(id: UUID, dto: ProductUpdate):
        # exige al menos un campo
        if not any(v is not None for v in dto.model_dump().values()):
            raise HTTPException(status_code=400, detail={"error": "ValidationError", "details": ["empty payload"]})
        p = await repo.update_partial(id, dto)
        if not p:
            raise NotFound()
        return p

    @r.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_product(id: UUID):
        removed = await repo.delete(id)
        if not removed:
            raise NotFound()

    return r
