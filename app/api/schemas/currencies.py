
import datetime
from pydantic import ConfigDict, Field
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


class CurrenciesToExchange(CustomModel):
    from_currency_code: str
    to_currency_code: str
    count: float = Field(gt=0, description="The count must be greater than zero")


class ConvertedCurrencies(CurrenciesToExchange):
    value: float
