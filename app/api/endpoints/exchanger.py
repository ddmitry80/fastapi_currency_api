import datetime
from typing import List
from fastapi import APIRouter
from app.api.dependencies.db import UOWDep
from app.api.schemas.currencies import CurrencyCreate

from app.api.schemas.rates import RateFromAPI, RatesUpdateStatus
from app.services.currency import CurrencyService
from app.services.network import NetworkService
from app.services.rate import RateService


router = APIRouter(
    prefix="/api",
    tags=["Currency exchange"],
)


@router.get("/update_rates")
async def update_rates(uow: UOWDep) -> RatesUpdateStatus:
    currencies_list: List[CurrencyCreate] = await NetworkService().fetch_currencies()
    rates_list: List[RateFromAPI] = await NetworkService().fetch_rates()
    updated_at=datetime.datetime.utcnow()

    await CurrencyService.refresh_list(currencies_list)
    await RateService.add_list(rates_list)
    
    return RatesUpdateStatus(status=True, updated_at=updated_at)
