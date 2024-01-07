import datetime
import logging
from typing import List
from fastapi import APIRouter
from app.api.dependencies.db import UOWDep
from app.api.schemas.currencies import CurrencyCreate

from app.api.schemas.rates import RateFromAPI, RatesUpdateStatus
from app.services.currency import CurrencyService
from app.services.network import NetworkService
from app.services.rate import RateService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Currency exchange"],
)


@router.get("/update_rates")
async def update_rates(uow: UOWDep) -> RatesUpdateStatus:
    currencies_list: List[CurrencyCreate] = await NetworkService().fetch_currencies()
    rates_list: List[RateFromAPI] = await NetworkService().fetch_rates()
    updated_at=datetime.datetime.utcnow()

    print(f"{currencies_list=}")
    print(f"{rates_list=}")

    currencies_added = await CurrencyService.refresh_list(uow=uow, currencies_list=currencies_list)
    rates_refreshed = await RateService.add_list(uow=uow, rates_list=rates_list)

    refresh_status = True if rates_refreshed > 0 else False
    
    response = RatesUpdateStatus(
        status=refresh_status, 
        updated_at=updated_at, 
        currencies_added=currencies_added, 
        rates_refreshed=rates_refreshed
        )
    logger.debug("update_rates: response=%s", response.to_log())
    return response
