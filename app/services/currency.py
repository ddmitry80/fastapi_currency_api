import logging
from typing import List
from app.api.schemas.currencies import CurrencyCreate, CurrencyFromDB
from app.utils.unitofwork import IUnitOfWork

logger = logging.getLogger(__name__)

class CurrencyService:
    async def add_currency(self, uow: IUnitOfWork, currency: CurrencyCreate) -> int:
        currency_dict: dict = currency.model_dump()
        async with uow:
            currency_from_db = await uow.currency.add_one(currency_dict)
            await uow.commit()
            return currency_from_db.id

    async def get_currency(self, uow: IUnitOfWork, code: str) -> CurrencyFromDB:
        async with uow:
            currency = await uow.currency.fetch_one(code=code)
            return currency

    async def refresh_list(self, uow: IUnitOfWork, currencies_list: List[CurrencyCreate]) -> int:
        """Обновляет список валют в БД, возвращает количество добавленных валют"""
        counter = 0
        async with uow:
            for currency in currencies_list:
                curr = await uow.currency.fetch_one(code=currency.code)
                if curr is None:
                    curr = await uow.currency.add_one(currency)
                    counter += 1
            await uow.commit()
        if counter > 0:
            logger.info("CurrencyService.refresh_list: added %s currencies", counter)
        else:
            logger.debug("CurrencyService.refresh_list: no new currencies")
        return counter