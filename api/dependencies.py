from fastapi import Depends
from sqlalchemy.orm import Session

from db.session import get_db
from service.habit import HabitService


def get_habit_service(db: Session = Depends(get_db)):
    return HabitService(db)