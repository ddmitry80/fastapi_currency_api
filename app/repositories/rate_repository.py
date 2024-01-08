import logging
from typing import Any
from app.api.schemas.currencies import CurrencyFromDB
from app.api.schemas.rates import RateFromAPI, RateFromDB
from app.db.models import Rate
from app.repositories.base_repository import Repository


logger = logging.getLogger(__name__)


class RateRepository(Repository):
    model = Rate
