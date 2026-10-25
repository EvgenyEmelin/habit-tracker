from pydantic import BaseModel, ConfigDict, Field


class HabitSchema(BaseModel):
    id: str
    name: str
    checked_today: bool

    model_config = ConfigDict(from_attributes=True)


class HabitCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class HabitUpdateSchema(BaseModel):
    checked_today: bool