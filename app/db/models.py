from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.api.schemas.auth import UserFromDB

from app.db.database import Base


class User(Base):
    __tablename__ = "auth_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(LargeBinary, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, onupdate=func.now(), nullable=True)

    def to_pydantic_model(self) -> UserFromDB:
        return UserFromDB.model_validate(self)
