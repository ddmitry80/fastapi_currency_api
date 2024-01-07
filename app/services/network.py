from typing import List
import aiohttp
from app.api.schemas.currencies import CurrencyCreate
from app.api.schemas.rates import RateFromAPI
from app.core.config import settings
from app.utils.exceptions import ExternalApiException

class NetworkService:
    def __init__(self):
        self.base_url = "http://exchangeratesapi.io/v1/"
        self.path_currencies = "symbols"
        self.path_rates = "latest"
        self.api_key = settings.EXCHANGE_API_KEY
    
    @property
    def _url_currencies(self) -> str:
        return f"{self.base_url}{self.path_currencies}?access_key={self.api_key}"
    
    @property
    def _url_rates(self) -> str:
        return f"{self.base_url}{self.path_rates}?access_key={self.api_key}"
    
    @staticmethod
    async def _fetch_data(url: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if response.status == 200:
                    return data
                else:
                    raise ExternalApiException(status_code=response.status, detail=data)    

    async def fetch_currencies(self) -> List[CurrencyCreate]:
        data: dict = await self._fetch_data(self._url_currencies)
        if data.get("symbols"):
            currencies = []
            for code, name in data["symbols"].items():
                currencies.append(CurrencyCreate(code=code, name=name))
            return currencies

    async def fetch_rates(self) -> List[RateFromAPI]:
        data: dict = await self._fetch_data(self._url_rates)
        if data.get("rates"):
            rates = []
            for currency, rate in data["rates"].items():
                rates.append(RateFromAPI(currency=currency, rate=rate))
            return rates
