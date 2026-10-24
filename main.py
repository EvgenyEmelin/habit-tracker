from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routers.habits import router as habit_router
from db.session import engine
from models.habits import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(habit_router)


