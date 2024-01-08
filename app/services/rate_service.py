import datetime
import logging
from typing import List
from app.api.schemas.currencies import CurrencyFromDB
from app.api.schemas.rates import RateCreate, RateFromAPI, RateFromDB

from app.utils.unitofwork import IUnitOfWork


logger = logging.getLogger(__name__)


class RateService:
    @staticmethod
    async def add_rate(uow: IUnitOfWork, rate: RateFromAPI, auto_session=True) -> int | None:
        rate_dict: dict = rate.model_dump()
        if auto_session:
            async with uow:
                currency: CurrencyFromDB = await uow.currency.fetch_one(code=rate.currency)
                if not currency:
                    # Не обнаружено валюты, на которую сохряняем курс
                    return None
                new_rate = RateCreate(currency_id=currency.id, rate=rate.rate)
                rate_from_db = await uow.rate.add_one(new_rate)
                await uow.commit()
        else:
            currency: CurrencyFromDB = await uow.currency.fetch_one(code=rate.currency)
            if not currency:
                # Не обнаружено валюты, на которую сохряняем курс
                return None
            new_rate = RateCreate(currency_id=currency.id, rate=rate.rate)
            rate_from_db = await uow.rate.add_one(new_rate)
        return rate_from_db

    @staticmethod
    async def get_rate(uow: IUnitOfWork, code: str) -> RateFromDB:
        async with uow:
            rate = await uow.rate.find_one(code=code)
        return rate

    @staticmethod
    async def add_list(uow: IUnitOfWork, rates_list: List[RateFromAPI]) -> int:
        counter = 0
        async with uow:
            for rate in rates_list:
                rate_from_db = await RateService.add_rate(uow, rate, auto_session=False)
                if rate_from_db:
                    counter += 1
            await uow.commit()
        logger.debug("RateService.add_list: added %s rates", counter)
        return counter
    
    @staticmethod
    async def get_max_datetime(uow: IUnitOfWork) -> datetime.datetime | None:
        async with uow:
            most_fresh_update = await uow.rate.find_max_value(field_name="updated_at")

        logger.debug("get_max_datetime: result=%s", most_fresh_update)
        return most_fresh_update
        