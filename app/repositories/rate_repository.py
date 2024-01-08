import logging
from typing import Any

from sqlalchemy import text
from app.api.schemas.currencies import CurrencyFromDB
from app.api.schemas.rates import RateFromAPI, RateFromDB
from app.db.models import Rate
from app.repositories.base_repository import Repository


logger = logging.getLogger(__name__)


class RateRepository(Repository):
    model = Rate

    async def find_latest_rate(self, code: str) -> RateFromDB | None:
        logger.debug("CurrencyRepository.find_latest_rate: code=%s", code)
        query = text("""
            WITH latest_update AS (
                SELECT currency_id, MAX(rate.updated_at) AS max_updated_at
                FROM rate
                GROUP BY rate.currency_id
            ), latest_rates AS (
                SELECT r.id, r.currency_id, r.rate, r.created_at, r.updated_at
                FROM latest_update AS lu
                INNER JOIN rate AS r
                    ON lu.currency_id = r.currency_id
                    AND lu.max_updated_at = r.updated_at
            ), rates_currencies AS (
                SELECT r.id, r.currency_id, r.rate, r.created_at, r.updated_at, c.code
                FROM latest_rates AS r
                INNER JOIN currency AS c
                    ON r.currency_id = c.id
            )
            SELECT id, currency_id, rate, created_at, updated_at 
            FROM rates_currencies
            WHERE code = :code
        """)
        rate = (await self.session.execute(query.bindparams(code=code))).fetchone()
        result = RateFromDB.model_validate(rate._asdict()) if rate else None

        logger.debug("CurrencyRepository.find_latest_rate: result=%s", result.to_log() if result else None)
        return result
