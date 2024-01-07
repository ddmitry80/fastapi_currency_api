from typing import List
from fastapi import APIRouter
from app.api.dependencies.db import UOWDep
from app.api.schemas.currencies import CurrencyCreate

from app.api.schemas.rates import RateCreate, RatesUpdateStatus
from app.services.network import NetworkService


router = APIRouter(
    prefix="/api",
    tags=["Currency exchange"],
)


@router.get("/update_rates", response_model=RatesUpdateStatus)
async def update_rates(uow: UOWDep):
    currencies_list: List[CurrencyCreate] = await NetworkService().fetch_currencies()
    rates_list: List[RateCreate] = await NetworkService().fetch_rates()

    for currency in currencies_list:
        try:
            await CurrencyService().add_currency(uow, currency)
        except IntegrityError:
            pass
    for rate in rates_list:
        await RateService().add_rate(uow, rate)
        updated_at: datetime.datetime = rate.updated_at
    return {"status": True, "updated_at": updated_at}
