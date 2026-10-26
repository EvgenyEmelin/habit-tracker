import datetime as dt
from typing import Annotated

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class HabitLogCreate(BaseModel):
    date: dt.date | None = None
    note: str | None = Field(default=None, max_length=500)


class HabitLogUpdate(BaseModel):
    note: str | None = Field(default=None, max_length=500)


class HabitLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    habit_id: str
    date: Annotated[dt.date, Field(validation_alias=AliasChoices("date", "date_local"))]
    note: str | None
    created_at: dt.datetime


class HabitLogList(BaseModel):
    items: list[HabitLogRead]
    total: int
    limit: int
    offset: int