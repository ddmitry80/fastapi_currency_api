import logging
from logging import config as logging_config

logging_config.fileConfig('logging.ini')
print(f"module {__name__} logging has configured")

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.dependencies.db import UOWDep
from app.db.database import init_db_schema
from app.services.user import UserService
from app.api.routers.routers import all_routers

logger = logging.getLogger(__name__)

app = FastAPI(
    tilte = "Currency exchange app"
)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_origin_regex=settings.CORS_ORIGINS_REGEX,
#     allow_credentials=True,
#     allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
#     allow_headers=settings.CORS_HEADERS,
# )

def includer_routers():
    logger.debug("Инициализация роутов")
    for router in all_routers:
        # continue
        app.include_router(router)

includer_routers()


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Currency Exchange Rates API server"}


@app.get("/healthcheck", include_in_schema=True)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get('/create_ddl')
async def create_ddl(uow: UOWDep):
    await init_db_schema()
    await UserService.insert_test_data(uow=uow)
    logger.info(f"create_ddl: ok")
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
