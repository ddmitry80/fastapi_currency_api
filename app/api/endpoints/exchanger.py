import datetime
import logging
from typing import List
from fastapi import APIRouter
from app.api.dependencies.db import UOWDep
from app.api.schemas.currencies import ConvertedCurrencies, CurrenciesToExchange, CurrencyCreate

from app.api.schemas.rates import RateFromAPI, RatesLastUpdateResponse, RatesUpdateStatus
from app.services.currency_service import CurrencyService
from app.services.network_service import NetworkService
from app.services.rate_service import RateService


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


@router.get("/last_update")
async def get_last_update_datetime(uow: UOWDep) -> RatesLastUpdateResponse:
    max_datetime = await RateService.get_max_datetime(uow)
    result = RatesLastUpdateResponse(updated_at=max_datetime)

    logger.debug("get_last_update_datetime: result=%s", result.to_log())
    return result


@router.post("/convert")
async def convert_currencies(uow: UOWDep, currencies_to_exchange: CurrenciesToExchange) -> ConvertedCurrencies:
    converted_currencies = await CurrencyService.convert_currencies(uow, currencies_to_exchange)
    return converted_currencies
