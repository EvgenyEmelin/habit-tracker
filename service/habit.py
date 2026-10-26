from datetime import date, timedelta

from config import today_local
from db.session import DbSession
from models.habits import HabitORM
from repositories.habit import HabitRepository
from repositories.habit_log import HabitLogRepository
from schemas.habits import HabitCreateSchema, HabitSchema, HabitUpdateSchema


class HabitNotFound(Exception):
    pass


class HabitService:
    def __init__(self, db: DbSession) -> None:
        self.db = db
        self.habit_repository = HabitRepository(db)
        self.habit_log_repository = HabitLogRepository(db)

    # ---------- чтение ----------

    def list_habits(self) -> list[HabitSchema]:
        return [self._to_schema(h) for h in self.habit_repository.get_all()]

    def get_habit(self, habit_id: str) -> HabitSchema:
        return self._to_schema(self._get_or_raise(habit_id))

    # ---------- запись ----------

    def create_habit(self, habit_create: HabitCreateSchema) -> HabitSchema:
        habit_orm = self.habit_repository.create(name=habit_create.name)
        self.db.commit()
        return self._to_schema(habit_orm)

    def update_habit(self, habit_id: str, habit_update: HabitUpdateSchema) -> HabitSchema:
        habit_orm = self._get_or_raise(habit_id)
        if habit_update.name is not None:
            habit_orm.name = habit_update.name
            self.db.commit()
        return self._to_schema(habit_orm)

    def delete_habit(self, habit_id: str) -> None:
        habit_orm = self._get_or_raise(habit_id)
        self.habit_repository.delete(habit_orm)
        self.db.commit()

    # ---------- отметки выполнения ----------

    def mark_completed(self, habit_id: str, day: date | None = None) -> HabitSchema:
        habit_orm = self._get_or_raise(habit_id)
        day = day or today_local()
        if not self.habit_log_repository.exists_on(habit_id, day):
            self.habit_log_repository.create(habit_id=habit_id, date_local=day)
            self.db.commit()
        return self._to_schema(habit_orm)

    def unmark_completed(self, habit_id: str, day: date | None = None) -> HabitSchema:
        habit_orm = self._get_or_raise(habit_id)
        day = day or today_local()
        log = self.habit_log_repository.get_by_habit_and_date(habit_id, day)
        if log is not None:
            self.habit_log_repository.delete(log)
            self.db.commit()
        return self._to_schema(habit_orm)

    # ---------- внутреннее ----------

    def _get_or_raise(self, habit_id: str) -> HabitORM:
        habit_orm = self.habit_repository.get_by_id(habit_id=habit_id)
        if habit_orm is None:
            raise HabitNotFound
        return habit_orm

    def _to_schema(self, habit_orm: HabitORM) -> HabitSchema:
        today = today_local()
        dates = self.habit_log_repository.dates_for(habit_orm.id)
        checked_today = today in dates
        current_streak, max_streak = self._streaks(dates, today)
        return HabitSchema(
            id=habit_orm.id,
            name=habit_orm.name,
            created_at=habit_orm.created_at,
            checked_today=checked_today,
            current_streak=current_streak,
            max_streak=max_streak,
        )

    @staticmethod
    def _streaks(dates: list[date], today: date) -> tuple[int, int]:
        if not dates:
            return 0, 0

        max_streak = cur = 1
        for prev, nxt in zip(dates, dates[1:]):
            if nxt - prev == timedelta(days=1):
                cur += 1
                max_streak = max(max_streak, cur)
            else:
                cur = 1

        tail = dates[-1]
        if tail not in (today, today - timedelta(days=1)):
            return 0, max_streak

        current_streak = 1
        for prev, nxt in zip(reversed(dates[:-1]), reversed(dates)):
            if nxt - prev == timedelta(days=1):
                current_streak += 1
            else:
                break
        return current_streak, max_streak