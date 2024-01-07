from app.api.schemas.currencies import CurrencyCreate, CurrencyFromDB
from app.utils.unitofwork import IUnitOfWork


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
