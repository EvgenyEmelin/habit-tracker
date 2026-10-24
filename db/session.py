from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, echo=settings.debug, pool_pre_ping=True)

SessionLocal = sessionmaker(engine, expire_on_commit=False)

def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

DbSession = Annotated[SessionLocal, Depends(get_db)]