from datetime import datetime

from pydantic import BaseModel, Field


class HabitSchema(BaseModel):
    id: str
    name: str
    created_at: datetime
    checked_today: bool
    current_streak: int
    max_streak: int


class HabitCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class HabitUpdateSchema(BaseModel):
    name: str | None = None