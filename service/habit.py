from db.session import DbSession
from repositories.habit import HabitRepository
from schemas.habits import HabitCreateSchema, HabitSchema, HabitUpdateSchema


class HabitNotFound(Exception):
    pass

class HabitService:

    def __init__(self, db: DbSession) -> None:
        self.db = db
        self.habit_repository = HabitRepository(db)

    def list_habits(self) -> list[HabitSchema]:
        habit_orm = self.habit_repository.get_all()
        return [HabitSchema.model_validate(habit) for habit in habit_orm]

    def create_habit(self, habit_create: HabitCreateSchema) -> HabitSchema:
        habit_orm = self.habit_repository.create(name=habit_create.name)
        self.db.commit()
        return HabitSchema.model_validate(habit_orm)

    def update_habit(self, habit_id :str ,habit_update: HabitUpdateSchema) -> HabitSchema:
        habit_for_update = self.habit_repository.get_by_id(habit_id=habit_id)
        if habit_update.checked_today is  None:
            raise HabitNotFound
        habit_for_update.checked_today = habit_update.checked_today
        self.db.commit()
        return HabitSchema.model_validate(habit_for_update)

    def delete_habit(self, habit_id: str) -> None:
        habit_for_delete = self.habit_repository.get_by_id(habit_id=habit_id)
        if habit_for_delete is None:
            raise HabitNotFound
        self.habit_repository.delete(habit_for_delete)
        self.db.commit()
