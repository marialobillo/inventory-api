# app/models.py
from __future__ import annotations
from datetime import datetime
from typing import Annotated
from sqlalchemy import String, Integer, Numeric, DateTime, func, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

PKStr = Annotated[str, mapped_column(String(36), primary_key=True)]     
NameStr = Annotated[str, mapped_column(String(200), nullable=False)]
PriceNum = Annotated[float, mapped_column(Numeric(10, 2), nullable=False)]
StockInt = Annotated[int, mapped_column(Integer, nullable=False)]

class Product(Base):
    __tablename__ = "products"

    id: Mapped[PKStr]
    name: Mapped[NameStr]
    price: Mapped[PriceNum]
    stock: Mapped[StockInt]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

Index("ix_products_name", Product.name)
