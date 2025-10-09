from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from app.core.config import settings
from app.connections.rabbitmq import rabbitmq
from app.api.main import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq.connect()
    app.state.rabbitmq = rabbitmq
    yield
    await rabbitmq.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

app.include_router(api_router)
