from datetime import date

from sqlalchemy import func, select

from db.session import DbSession
from models.habits import HabitLogsORM


class HabitLogRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def get_by_habit_and_date(
        self, habit_id: str, date_local: date
    ) -> HabitLogsORM | None:
        stmt = select(HabitLogsORM).where(
            HabitLogsORM.habit_id == habit_id,
            HabitLogsORM.date_local == date_local,
        )
        return self.db.scalar(stmt)

    def create(
        self, habit_id: str, date_local: date, note: str | None = None
    ) -> HabitLogsORM:
        log = HabitLogsORM(habit_id=habit_id, date_local=date_local, note=note)
        self.db.add(log)
        self.db.flush()
        return log

    def update_note(self, log: HabitLogsORM, note: str | None) -> HabitLogsORM:
        log.note = note
        self.db.flush()
        return log

    def delete(self, log: HabitLogsORM) -> None:
        self.db.delete(log)
        self.db.flush()

    def dates_for(self, habit_id: str) -> list[date]:
        stmt = (
            select(HabitLogsORM.date_local)
            .where(HabitLogsORM.habit_id == habit_id)
            .order_by(HabitLogsORM.date_local)
        )
        return list(self.db.scalars(stmt))

    def list_logs(
        self,
        habit_id: str,
        from_date: date,
        to_date: date,
        limit: int,
        offset: int,
    ) -> tuple[list[HabitLogsORM], int]:
        base = select(HabitLogsORM).where(
            HabitLogsORM.habit_id == habit_id,
            HabitLogsORM.date_local >= from_date,
            HabitLogsORM.date_local <= to_date,
        )
        total = int(
            self.db.scalar(select(func.count()).select_from(base.subquery())) or 0
        )
        items = list(
            self.db.scalars(
                base.order_by(HabitLogsORM.date_local.desc())
                .limit(limit)
                .offset(offset)
            )
        )
        return items, total

    def count_in_range(
        self, habit_id: str, from_date: date, to_date: date
    ) -> int:
        stmt = select(func.count()).where(
            HabitLogsORM.habit_id == habit_id,
            HabitLogsORM.date_local >= from_date,
            HabitLogsORM.date_local <= to_date,
        )
        return int(self.db.scalar(stmt) or 0)