from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies import get_habit_service
from schemas.habits import HabitCreateSchema, HabitSchema, HabitUpdateSchema
from service.habit import HabitNotFound, HabitService

router = APIRouter(prefix="/api")


@router.get("/habits", response_model=list[HabitSchema])
def get_habits(
    habit_service: HabitService = Depends(get_habit_service),
) -> list[HabitSchema]:
    return habit_service.list_habits()


@router.post("/habits", status_code=status.HTTP_201_CREATED, response_model=HabitSchema)
def create_habit(
    payload: HabitCreateSchema,
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitSchema:
    return habit_service.create_habit(habit_create=payload)


@router.patch("/habits/{habit_id}", response_model=HabitSchema)
def update_habit(
    habit_id: str,
    payload: HabitUpdateSchema,
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitSchema:
    try:
        return habit_service.update_habit(habit_id=habit_id, habit_update=payload)
    except HabitNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )


@router.delete("/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: str,
    habit_service: HabitService = Depends(get_habit_service),
) -> None:
    try:
        habit_service.delete_habit(habit_id=habit_id)
    except HabitNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )


# ---------- отметки выполнения ----------

@router.post("/habits/{habit_id}/check", response_model=HabitSchema)
def mark_completed(
    habit_id: str,
    day: date | None = Query(None, description="По умолчанию — сегодня"),
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitSchema:
    try:
        return habit_service.mark_completed(habit_id=habit_id, day=day)
    except HabitNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )


@router.delete("/habits/{habit_id}/check", response_model=HabitSchema)
def unmark_completed(
    habit_id: str,
    day: date | None = Query(None, description="По умолчанию — сегодня"),
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitSchema:
    try:
        return habit_service.unmark_completed(habit_id=habit_id, day=day)
    except HabitNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )