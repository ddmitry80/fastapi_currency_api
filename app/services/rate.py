import logging
from typing import List
from app.api.schemas.currencies import CurrencyFromDB
from app.api.schemas.rates import RateCreate, RateFromAPI, RateFromDB

from app.utils.unitofwork import IUnitOfWork


logger = logging.getLogger(__name__)


class RateService:
    @staticmethod
    async def add_rate(uow: IUnitOfWork, rate: RateFromAPI) -> int | None:
        rate_dict: dict = rate.model_dump()
        async with uow:
            currency: CurrencyFromDB = await uow.currency.fetch_one(code=rate.currency)
            if not currency:
                # Не обнаружено валюты, на которую сохряняем курс
                return None
            new_rate = RateCreate(currency_id=currency.id, rate=rate.rate)
            rate_from_db = await uow.rate.add_one(new_rate)
            await uow.commit()
        return rate_from_db

    @staticmethod
    async def get_rate(uow: IUnitOfWork, code: str) -> RateFromDB:
        async with uow:
            rate = await uow.rate.find_one(code=code)
        return rate

    @staticmethod
    async def add_list(uow: IUnitOfWork, rates_list: List[RateFromAPI]) -> int:
        counter = 0
        for rate in rates_list:
            rate_from_db = await RateService.add_rate(uow, rate)
            if rate_from_db:
                counter += 1
        
        logger.debug("RateService.add_list: added %s rates", counter)
        return counter
        