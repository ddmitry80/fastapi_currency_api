
import datetime
from pydantic import ConfigDict
from app.api.schemas.custom_model import CustomModel


class CurrencyCreate(CustomModel):
    name: str
    code: str


class CurrencyFromDB(CustomModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None
