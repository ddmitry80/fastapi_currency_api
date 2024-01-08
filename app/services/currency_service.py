import logging
from typing import List
from app.api.schemas.currencies import CurrencyCreate, CurrencyFromDB
from app.utils.unitofwork import IUnitOfWork

logger = logging.getLogger(__name__)

class CurrencyService:
    @staticmethod
    async def add_currency(uow: IUnitOfWork, currency: CurrencyCreate) -> int:
        # currency_dict: dict = currency.model_dump()
        async with uow:
            currency_from_db = await uow.currency.add_one(currency)
            await uow.commit()
        return currency_from_db.id

    @staticmethod
    async def get_currency(uow: IUnitOfWork, code: str) -> CurrencyFromDB:
        async with uow:
            currency = await uow.currency.fetch_one(code=code)
            return currency

    @staticmethod
    async def refresh_list(uow: IUnitOfWork, currencies_list: List[CurrencyCreate]) -> int:
        """Обновляет список валют в БД, возвращает количество добавленных валют"""
        counter = 0
        async with uow:
            for currency in currencies_list:
                curr = await uow.currency.fetch_one(name=currency.name, code=currency.code)
                if curr is None:
                    curr = await uow.currency.add_one(currency)
                    counter += 1
                    print(f"added_currency: {curr!r}, {counter=}")
                else:
                    print(f"found currency: {curr!r}")
            await uow.commit()
        if counter > 0:
            logger.info("CurrencyService.refresh_list: added %s currencies", counter)
        else:
            logger.debug("CurrencyService.refresh_list: no new currencies")
        return counter