# app/repo_sqlalchemy.py
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func  # update no se usa, lo quitamos

from pydantic import UUID4, TypeAdapter  # 👈 para validar/castear a UUID4

from .repo import ProductRepository
from .domain import Product, ProductUpdate
from .models import Product as ProductORM

_uuid4 = TypeAdapter(UUID4)  # reutilizable

def _to_domain(row: ProductORM) -> Product:
    # id en ORM es str; validamos/casteamos a UUID4 para contentar a Pylance y garantizar versión
    uid: UUID4 = _uuid4.validate_python(row.id)
    price = float(row.price) if isinstance(row.price, Decimal) else float(row.price)
    return Product(id=uid, name=row.name, price=price, stock=row.stock)

class SqlAlchemyProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, p: Product) -> None:
        obj = ProductORM(
            id=str(p.id),  # almacenamos como texto en SQLite
            name=p.name,
            price=p.price,
            stock=p.stock,
        )
        self.session.add(obj)
        await self.session.commit()

    async def get(self, id: UUID) -> Optional[Product]:
        stmt = select(ProductORM).where(ProductORM.id == str(id))
        res = await self.session.execute(stmt)
        row = res.scalar_one_or_none()
        return _to_domain(row) if row else None

    async def list(
        self, limit: int | None = None, offset: int = 0, q: str | None = None
    ) -> List[Product]:
        stmt = select(ProductORM)
        if q:
            ql = f"%{q.lower()}%"
            stmt = stmt.where(func.lower(ProductORM.name).like(ql))
        stmt = stmt.order_by(ProductORM.created_at.desc())
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        res = await self.session.execute(stmt)
        rows = res.scalars().all()
        return [_to_domain(r) for r in rows]

    async def update_partial(self, id: UUID, patch: ProductUpdate) -> Optional[Product]:
        stmt = select(ProductORM).where(ProductORM.id == str(id))
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj:
            return None
        data = patch.model_dump(exclude_unset=True)
        if "name" in data and data["name"] is not None:
            obj.name = data["name"]
        if "price" in data and data["price"] is not None:
            obj.price = data["price"]
        if "stock" in data and data["stock"] is not None:
            obj.stock = data["stock"]
        await self.session.commit()
        await self.session.refresh(obj)
        return _to_domain(obj)

    async def delete(self, id: UUID) -> bool:
        stmt = delete(ProductORM).where(ProductORM.id == str(id))
        res = await self.session.execute(stmt)
        await self.session.commit()
        # aseguremos bool estricto:
        return (res.rowcount or 0) > 0
