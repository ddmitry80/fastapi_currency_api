import logging
from logging import config as logging_config
logging_config.fileConfig('logging.ini')

from app.api.dependencies.db import UOWDep
from app.db.database import init_db_schema
from app.services.user import UserService

import uvicorn
from fastapi import FastAPI

from app.api.routers.routers import all_routers

logger = logging.getLogger(__name__)
app = FastAPI(
    tilte = "Currency exchange app"
)

logger.debug("Инициализация роутов")
for router in all_routers:
    # continue
    app.include_router(router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Currency Exchange Rates API server"}


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get('/create_ddl')
async def create_ddl(uow: UOWDep):
    await init_db_schema()
    await UserService.insert_mock_data(uow=uow)
    logger.info(f"create_ddl: ok")
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
