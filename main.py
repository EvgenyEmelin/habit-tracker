from fastapi import FastAPI

from api.routers.habits import router as habit_router

app = FastAPI()

app.include_router(habit_router)


