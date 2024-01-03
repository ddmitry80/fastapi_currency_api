import uvicorn
from fastapi import FastAPI

from app.api.endpoints.todo import todo_router


app = FastAPI()

app.include_router(todo_router)


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
