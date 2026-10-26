from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from api.dependencies import get_habit_service
from schemas.habit_log import (
    HabitLogCreate,
    HabitLogList,
    HabitLogRead,
    HabitLogUpdate,
)
from schemas.habits import HabitCreateSchema, HabitSchema, HabitUpdateSchema
from schemas.stats import HabitStats
from service.habit import (
    HabitLogFutureDate,
    HabitLogNotFound,
    HabitNotFound,
    HabitService,
)

router = APIRouter(prefix="/api")


# ---------- habits ----------

@router.get("/habits", response_model=list[HabitSchema])
def get_habits(
    habit_service: HabitService = Depends(get_habit_service),
) -> list[HabitSchema]:
    return habit_service.list_habits()


@router.post(
    "/habits", status_code=status.HTTP_201_CREATED, response_model=HabitSchema
)
def create_habit(
    payload: HabitCreateSchema,
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitSchema:
    return habit_service.create_habit(habit_create=payload)


@router.get("/habits/{habit_id}", response_model=HabitSchema)
def get_habit(
    habit_id: str,
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitSchema:
    try:
        return habit_service.get_habit(habit_id=habit_id)
    except HabitNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )


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
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )


# ---------- logs ----------

@router.post("/habits/{habit_id}/logs", response_model=HabitLogRead)
def create_habit_log(
    habit_id: str,
    payload: HabitLogCreate,
    response: Response,
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitLogRead:
    try:
        log, created = habit_service.create_log(habit_id, payload)
    except HabitNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )
    except HabitLogFutureDate:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date in the future",
        )
    response.status_code = (
        status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )
    return log


@router.patch(
    "/habits/{habit_id}/logs/{log_date}", response_model=HabitLogRead
)
def update_habit_log(
    habit_id: str,
    log_date: date,
    payload: HabitLogUpdate,
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitLogRead:
    try:
        return habit_service.update_log(habit_id, log_date, payload)
    except HabitNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )
    except HabitLogNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log not found"
        )


@router.delete(
    "/habits/{habit_id}/logs/{log_date}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_habit_log(
    habit_id: str,
    log_date: date,
    habit_service: HabitService = Depends(get_habit_service),
) -> None:
    try:
        habit_service.delete_log(habit_id, log_date)
    except HabitNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )
    except HabitLogNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log not found"
        )


@router.get("/habits/{habit_id}/logs", response_model=HabitLogList)
def list_habit_logs(
    habit_id: str,
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitLogList:
    try:
        return habit_service.list_logs(
            habit_id, from_date, to_date, limit, offset
        )
    except HabitNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )


# ---------- stats ----------

@router.get("/habits/{habit_id}/stats", response_model=HabitStats)
def get_habit_stats(
    habit_id: str,
    period: Literal["week", "month", "year", "all"] = Query("month"),
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitStats:
    try:
        return habit_service.get_stats(habit_id, period, from_date, to_date)
    except HabitNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )