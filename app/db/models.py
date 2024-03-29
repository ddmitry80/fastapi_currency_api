from __future__ import annotations
from datetime import datetime
from typing import List
from pydantic import UUID4

from sqlalchemy import UUID, BigInteger, Boolean, DateTime, ForeignKey, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.api.schemas.auth import JWTData, UserFromDB, UserRefreshTokenFromDB
from app.api.schemas.currencies import CurrencyFromDB
from app.api.schemas.rates import RateFromDB

from app.db.database import Base


class User(Base):
    __tablename__ = "auth_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(LargeBinary, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    tokens: Mapped[List[UserRefreshToken]] = relationship(back_populates="user")

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def to_pydantic_model(self) -> UserFromDB:
        return UserFromDB.model_validate(self)


class UserRefreshToken(Base):
    __tablename__ = "auth_refresh_token"

    uuid: Mapped[UUID4] = mapped_column(UUID, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    user: Mapped[User] = relationship(back_populates="tokens")

    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def to_pydantic_model(self) -> UserFromDB:
        return UserRefreshTokenFromDB.model_validate(self)
    

class Currency(Base):
    __tablename__ = "currency"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    rates: Mapped[List[Rate]] = relationship("Rate", back_populates="currency")

    def to_pydantic_model(self) -> CurrencyFromDB:
        return CurrencyFromDB.model_validate(self)


class Rate(Base):
    __tablename__ = "rate"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    currency_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Currency.id, ondelete='CASCADE'), nullable=False)
    rate: Mapped[float]

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    currency: Mapped[Currency] = relationship(Currency, back_populates="rates")

    def to_pydantic_model(self):
        return RateFromDB.model_validate(self)
