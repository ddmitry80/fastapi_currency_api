from contextlib import asynccontextmanager
from httpx import AsyncClient
from fastapi import Response, status
import pytest
import datetime

from app.api.schemas.currencies import CurrencyCreate
from app.api.schemas.rates import RateCreate, RateFromAPI, RatesLastUpdateResponse
from app.services.currency_service import CurrencyService
from app.services.network_service import NetworkService
from app.services.rate_service import RateService
from app.utils.unitofwork import UnitOfWork

# Отмечаю, что все тесте в файле - асинхронные, с anyio
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


async def test_latest_rate(with_uow: UnitOfWork, client: AsyncClient):
    rate = await with_uow.rate.find_latest_rate(code='USD')
    print(f"{rate.rate=}")
    assert rate.rate == 1.09475


async def test_get_las_update_datetime(async_db_sesstion, with_uow: UnitOfWork, client: AsyncClient):
    result: Response = await client.get("/api/last_update")
    assert result.status_code == status.HTTP_200_OK
    updated_at = result.json()["updated_at"]
    assert updated_at is not None
    dt_delta = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(updated_at)
    print(f"{updated_at=}, {dt_delta=}")
    assert  dt_delta < datetime.timedelta(seconds=60)


async def test_fetch_rates(client, monkeypatch):
   
    class MockAiohttpClientSessionGet:
        json_data = None
        status = None
        def __init__(*args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *error_info):
            return self
        async def json(self):
            return self.json_data
    
    class AsyncMockCurrencies(MockAiohttpClientSessionGet):
        json_data = {"symbols": {"USD": "US Dollar", "EUR": "Euro"}}
        status = 200

    class AsyncMockRates(MockAiohttpClientSessionGet):
        json_data = {"rates": {"USD": 1.1, "EUR": 1}}
        status = 200

    with monkeypatch.context() as m:
        m.setattr("aiohttp.ClientSession.get", AsyncMockCurrencies)
        currs = await NetworkService().fetch_currencies()
        m.setattr("aiohttp.ClientSession.get", AsyncMockRates)
        rates = await NetworkService().fetch_rates()
    # print(f"{currs=}, {rates=}")

    assert currs == [CurrencyCreate(name='US Dollar', code='USD'), CurrencyCreate(name='Euro', code='EUR')]
    assert rates == [RateFromAPI(rate=1.1, currency='USD'), RateFromAPI(rate=1.0, currency='EUR')]

