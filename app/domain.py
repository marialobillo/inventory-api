from typing import Optional
from pydantic import BaseModel, Field, UUID4

class ProductCreate(BaseModel):
    id: UUID4
    name: str = Field(min_length=1)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)

class Product(ProductCreate):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)
