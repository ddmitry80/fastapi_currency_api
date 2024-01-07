
import datetime

from pydantic import ConfigDict
from app.api.schemas.custom_model import CustomModel


class RateCreate(CustomModel):
    rate: float
    currency: str


class RateFromDB(CustomModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    currency_id: int
    rate: float
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None


class RatesLastUpdateResponse(CustomModel):
    updated_at: datetime.datetime | None


class RatesUpdateStatus(RatesLastUpdateResponse):
    status: bool
