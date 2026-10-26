from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.habits import HabitLogsORM


class HabitLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, habit_id: str, date_local: date) -> HabitLogsORM:
        log = HabitLogsORM(habit_id=habit_id, date_local=date_local)
        self.db.add(log)
        self.db.flush()
        return log

    def delete(self, log: HabitLogsORM) -> None:
        self.db.delete(log)
        self.db.flush()

    def get_by_habit_and_date(self, habit_id: str, date_local: date) -> HabitLogsORM | None:
        stmt = select(HabitLogsORM).where(
            HabitLogsORM.habit_id == habit_id,
            HabitLogsORM.date_local == date_local,
        )
        return self.db.scalar(stmt)

    def exists_on(self, habit_id: str, date_local: date) -> bool:
        return self.get_by_habit_and_date(habit_id, date_local) is not None

    def dates_for(self, habit_id: str) -> list[date]:
        stmt = (
            select(HabitLogsORM.date_local)
            .where(HabitLogsORM.habit_id == habit_id)
            .order_by(HabitLogsORM.date_local)
        )
        return list(self.db.scalars(stmt))