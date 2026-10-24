from pydantic import BaseModel, ConfigDict


class HabitSchema(BaseModel):
    id: str
    name: str
    checked_today: bool

    model_config = ConfigDict(from_attributes=True)


class HabitCreateSchema(BaseModel):
    name: str

class HabitUpdateSchema(BaseModel):
    checked_today: bool