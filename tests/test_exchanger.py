from httpx import AsyncClient
import pytest

from app.api.schemas.currencies import CurrencyCreate
from app.api.schemas.rates import RateCreate, RateFromAPI
from app.services.currency_service import CurrencyService
from app.services.rate_service import RateService
from app.utils.unitofwork import UnitOfWork

pytestmark = pytest.mark.anyio

@pytest.fixture(scope="session", autouse=True)
async def add_rates(with_uow):
    uow=with_uow
    usd = CurrencyCreate(name="United States Dollar", code="USD")
    eur = CurrencyCreate(name="Euro", code="EUR")
    curr_list = [usd, eur]
    usd_rate = RateFromAPI(rate=2.09475, currency='USD')
    eur_rate = RateFromAPI(rate=1, currency='EUR')
    rates_list = [usd_rate, eur_rate]

    await CurrencyService.refresh_list(uow, curr_list)
    await RateService.add_list(uow, rates_list)
    await uow.commit()

    usd_rate = RateFromAPI(rate=1.09475, currency='USD')
    eur_rate = RateFromAPI(rate=1, currency='EUR')
    rates_list = [usd_rate, eur_rate]
    await RateService.add_list(uow, rates_list)
    await uow.commit()


@pytest.mark.anyio
async def test_latest_rate(with_uow: UnitOfWork, client: AsyncClient):
    rate = await with_uow.rate.find_latest_rate(code='USD')
    print(f"{rate.rate=}")
    assert rate.rate == 1.09475
