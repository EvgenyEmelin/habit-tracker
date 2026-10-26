from datetime import date, timedelta

from config import today_local
from db.session import DbSession
from models.habits import HabitLogsORM, HabitORM
from repositories.habit import HabitRepository
from repositories.habit_log import HabitLogRepository
from schemas.habit_log import (
    HabitLogCreate,
    HabitLogList,
    HabitLogRead,
    HabitLogUpdate,
)
from schemas.habits import HabitCreateSchema, HabitSchema, HabitUpdateSchema
from schemas.stats import HabitStats


class HabitNotFound(Exception):
    pass


class HabitLogNotFound(Exception):
    pass


class HabitLogFutureDate(Exception):
    pass


WEEKDAY_NAMES = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


class HabitService:
    def __init__(self, db: DbSession) -> None:
        self.db = db
        self.habit_repository = HabitRepository(db)
        self.habit_log_repository = HabitLogRepository(db)

    # ---------- habits ----------

    def list_habits(self) -> list[HabitSchema]:
        return [self._to_schema(h) for h in self.habit_repository.get_all()]

    def get_habit(self, habit_id: str) -> HabitSchema:
        return self._to_schema(self._get_habit_or_raise(habit_id))

    def create_habit(self, habit_create: HabitCreateSchema) -> HabitSchema:
        habit_orm = self.habit_repository.create(name=habit_create.name)
        self.db.commit()
        return self._to_schema(habit_orm)

    def update_habit(
        self, habit_id: str, habit_update: HabitUpdateSchema
    ) -> HabitSchema:
        habit_orm = self._get_habit_or_raise(habit_id)
        if habit_update.name is not None:
            habit_orm.name = habit_update.name
            self.db.commit()
        return self._to_schema(habit_orm)

    def delete_habit(self, habit_id: str) -> None:
        habit_orm = self._get_habit_or_raise(habit_id)
        self.habit_repository.delete(habit_orm)
        self.db.commit()

    # ---------- logs ----------

    def create_log(
        self, habit_id: str, payload: HabitLogCreate
    ) -> tuple[HabitLogRead, bool]:
        """Возвращает (лог, created). created=True → 201, False → 200."""
        self._get_habit_or_raise(habit_id)
        today = today_local()
        day = payload.date or today

        if day > today:
            raise HabitLogFutureDate

        existing = self.habit_log_repository.get_by_habit_and_date(habit_id, day)
        if existing is not None:
            if "note" in payload.model_fields_set:
                self.habit_log_repository.update_note(existing, payload.note)
                self.db.commit()
            return self._log_to_schema(existing), False

        log = self.habit_log_repository.create(habit_id, day, payload.note)
        self.db.commit()
        return self._log_to_schema(log), True

    def update_log(
        self, habit_id: str, date_local: date, payload: HabitLogUpdate
    ) -> HabitLogRead:
        self._get_habit_or_raise(habit_id)
        log = self.habit_log_repository.get_by_habit_and_date(habit_id, date_local)
        if log is None:
            raise HabitLogNotFound
        if "note" in payload.model_fields_set:
            self.habit_log_repository.update_note(log, payload.note)
            self.db.commit()
        return self._log_to_schema(log)

    def delete_log(self, habit_id: str, date_local: date) -> None:
        self._get_habit_or_raise(habit_id)
        log = self.habit_log_repository.get_by_habit_and_date(habit_id, date_local)
        if log is None:
            raise HabitLogNotFound
        self.habit_log_repository.delete(log)
        self.db.commit()

    def list_logs(
        self,
        habit_id: str,
        from_date: date | None,
        to_date: date | None,
        limit: int,
        offset: int,
    ) -> HabitLogList:
        self._get_habit_or_raise(habit_id)
        today = today_local()
        to_d = to_date or today
        from_d = from_date or (to_d - timedelta(days=30))
        items, total = self.habit_log_repository.list_logs(
            habit_id, from_d, to_d, limit, offset
        )
        return HabitLogList(
            items=[self._log_to_schema(log) for log in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    # ---------- stats ----------

    def get_stats(
        self,
        habit_id: str,
        period: str,
        from_date: date | None,
        to_date: date | None,
    ) -> HabitStats:
        habit_orm = self._get_habit_or_raise(habit_id)
        today = today_local()

        if from_date is not None or to_date is not None:
            period = "custom"
            period_from = from_date or habit_orm.created_at.date()
            period_to = to_date or today
        else:
            if period == "week":
                period_from = today - timedelta(days=6)
                period_to = today
            elif period == "year":
                period_from = today - timedelta(days=364)
                period_to = today
            elif period == "all":
                period_from = habit_orm.created_at.date()
                period_to = today
            else:  # month (default)
                period = "month"
                period_from = today - timedelta(days=29)
                period_to = today

        created = habit_orm.created_at.date()
        effective_from = max(period_from, created)
        effective_to = min(period_to, today)
        total_days = max(0, (effective_to - effective_from).days + 1)

        completed_days = self.habit_log_repository.count_in_range(
            habit_id, effective_from, effective_to
        )
        rate = (completed_days / total_days) if total_days > 0 else 0.0

        dates = self.habit_log_repository.dates_for(habit_id)
        current_streak, max_streak = self._streaks(dates, today)

        by_weekday = {name: 0 for name in WEEKDAY_NAMES}
        for d in dates:
            if effective_from <= d <= effective_to:
                by_weekday[WEEKDAY_NAMES[d.weekday()]] += 1

        return HabitStats(
            habit_id=habit_id,
            period=period,
            period_from=effective_from,
            period_to=effective_to,
            total_days=total_days,
            completed_days=completed_days,
            completion_rate=rate,
            current_streak=current_streak,
            max_streak=max_streak,
            by_weekday=by_weekday,
        )

    # ---------- helpers ----------

    def _get_habit_or_raise(self, habit_id: str) -> HabitORM:
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
    def _log_to_schema(log: HabitLogsORM) -> HabitLogRead:
        return HabitLogRead(
            id=log.id,
            habit_id=log.habit_id,
            date=log.date_local,
            note=log.note,
            created_at=log.created_at,
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