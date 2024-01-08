import logging

from sqlalchemy import text
from app.api.schemas.rates import RateFromDB
from app.db.models import Currency
from app.repositories.base_repository import Repository


logger = logging.getLogger(__name__)


class CurrencyRepository(Repository):
    model = Currency


