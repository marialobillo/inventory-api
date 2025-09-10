from typing import Dict, List, Optional
from uuid import UUID
from .domain import Product, ProductUpdate

class ProductRepository:
    async def add(self, p: Product) -> None: ...
    async def get(self, id: UUID) -> Optional[Product]: ...
    async def list(self, limit: int | None = None, offset: int = 0, q: str | None = None) -> List[Product]: ...
    async def update_partial(self, id: UUID, patch: ProductUpdate) -> Optional[Product]: ...
    async def delete(self, id: UUID) -> bool: ...

class InMemoryProductRepository(ProductRepository):
    def __init__(self) -> None:
        self.store: Dict[UUID, Product] = {}

    async def add(self, p: Product) -> None:
        self.store[p.id] = p

    async def get(self, id: UUID) -> Optional[Product]:
        return self.store.get(id)

    async def list(self, limit: int | None = None, offset: int = 0, q: str | None = None) -> List[Product]:
        items = list(self.store.values())
        if q:
            ql = q.lower()
            items = [p for p in items if ql in p.name.lower()]
        # orden simple por nombre para estabilidad (o por id)
        items.sort(key=lambda p: p.name.lower())
        if offset:
            items = items[offset:]
        if limit is not None:
            items = items[:limit]
        return items

    async def update_partial(self, id: UUID, patch: ProductUpdate) -> Optional[Product]:
        cur = self.store.get(id)
        if not cur:
            return None
        data = cur.model_dump()
        data.update({k: v for k, v in patch.model_dump(exclude_unset=True).items() if v is not None})
        updated = Product(**data)
        self.store[id] = updated
        return updated

    async def delete(self, id: UUID) -> bool:
        return self.store.pop(id, None) is not None
