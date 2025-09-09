from typing import Dict, List, Optional
from uuid import UUID
from .domain import Product, ProductUpdate

class ProductRepository:
    async def add(self, p: Product) -> None: ...
    async def get(self, id: UUID) -> Optional[Product]: ...
    async def list(self) -> List[Product]: ...
    async def update_partial(self, id: UUID, patch: ProductUpdate) -> Optional[Product]: ...
    async def delete(self, id: UUID) -> bool: ...

class InMemoryProductRepository(ProductRepository):
    def __init__(self) -> None:
        self.store: Dict[UUID, Product] = {}

    async def add(self, p: Product) -> None:
        self.store[p.id] = p

    async def get(self, id: UUID) -> Optional[Product]:
        return self.store.get(id)

    async def list(self) -> List[Product]:
        return list(self.store.values())

    async def update_partial(self, id: UUID, patch: ProductUpdate) -> Optional[Product]:
        cur = self.store.get(id)
        if not cur:
            return None
        data = cur.model_dump()
        patch_data = {k: v for k, v in patch.model_dump(exclude_unset=True).items() if v is not None}
        data.update(patch_data)
        updated = Product(**data)
        self.store[id] = updated
        return updated

    async def delete(self, id: UUID) -> bool:
        return self.store.pop(id, None) is not None
