from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declared_attr


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))


class HabitORM(Base):
    __tablename__ = "habits"

    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    logs: Mapped[list["HabitLogsORM"]] = relationship(
        back_populates="habit",
        cascade="all, delete-orphan",
    )


class HabitLogsORM(Base):
    __tablename__ = "habit_logs"

    habit_id: Mapped[str] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"),
        nullable=False,
    )

    date_local: Mapped[date] = mapped_column(Date, nullable=False)

    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    habit: Mapped["HabitORM"] = relationship(back_populates="logs")

    @declared_attr
    def __table_args__(cls):
        return (
            UniqueConstraint("habit_id", "date_local", name="uq_habit_id_date_local"),
            Index("idx_habit_logs_query", "habit_id", cls.date_local.desc()),
        )