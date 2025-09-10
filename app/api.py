from fastapi import APIRouter, Depends, HTTPException, Query, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from .domain import ProductCreate, Product, ProductUpdate
from .repo import ProductRepository
from .repo_sqlalchemy import SqlAlchemyProductRepository
from .db import get_session
from .errors import AlreadyExists, NotFound

def get_repo(session: AsyncSession = Depends(get_session)) -> ProductRepository:
    return SqlAlchemyProductRepository(session)

def build_products_router() -> APIRouter:
    r = APIRouter(prefix="/products", tags=["products"])

    @r.post("", status_code=status.HTTP_201_CREATED)
    async def create_product(dto: ProductCreate, repo: ProductRepository = Depends(get_repo)):
        existing = await repo.get(dto.id)
        if existing:
            raise AlreadyExists()
        await repo.add(Product(**dto.model_dump()))
        return {}

    @r.get("", response_model=list[Product])
    async def list_products(
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
        q: str | None = Query(None, min_length=1),
        repo: ProductRepository = Depends(get_repo),
    ):
        return await repo.list(limit=limit, offset=offset, q=q)

    @r.get("/{id}", response_model=Product)
    async def get_product(id: UUID, repo: ProductRepository = Depends(get_repo)):
        p = await repo.get(id)
        if not p:
            raise NotFound()
        return p

    @r.patch("/{id}", response_model=Product)
    async def update_product(id: UUID, dto: ProductUpdate, repo: ProductRepository = Depends(get_repo)):
        if not any(v is not None for v in dto.model_dump().values()):
            raise HTTPException(status_code=400, detail={"error": "ValidationError", "details": ["empty payload"]})
        p = await repo.update_partial(id, dto)
        if not p:
            raise NotFound()
        return p

    @r.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_product(id: UUID, repo: ProductRepository = Depends(get_repo)):
        removed = await repo.delete(id)
        if not removed:
            raise NotFound()

    return r
