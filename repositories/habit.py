from sqlalchemy import select

from db.session import DbSession
from models.habits import HabitORM


class HabitRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def get_all(self) -> list[HabitORM]:
        return self.db.scalars(select(HabitORM)).all()

    def get_by_id(self, habit_id: str) -> HabitORM:
        return self.db.get(HabitORM, habit_id)

    def create(self, name: str) -> HabitORM:
        new_habit = HabitORM(name=name, checked_today=False)
        self.db.add(new_habit)
        self.db.flush()
        return new_habit

    def delete(self, habit: HabitORM) -> None:
        self.db.delete(habit)