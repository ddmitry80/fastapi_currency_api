import uvicorn
from fastapi import FastAPI

from app.api.routers.routers import all_routers


app = FastAPI(
    tilte = "Currency exchange app"
)

for router in all_routers:
    app.include_router(router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Currency Exchange Rates API server"}


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
