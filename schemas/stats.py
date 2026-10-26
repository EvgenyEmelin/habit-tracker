from datetime import date
from typing import Literal

from pydantic import BaseModel


class WeekdayBreakdown(BaseModel):
    mon: int = 0
    tue: int = 0
    wed: int = 0
    thu: int = 0
    fri: int = 0
    sat: int = 0
    sun: int = 0


class HabitStats(BaseModel):
    habit_id: str
    period: Literal["week", "month", "year", "all", "custom"]
    period_from: date
    period_to: date
    total_days: int
    completed_days: int
    completion_rate: float
    current_streak: int
    max_streak: int
    by_weekday: WeekdayBreakdown