# Описание моделей/таблиц БД

from sqlalchemy import MetaData
from .database import engine
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Text,
    Date,
)

meta = MetaData()

flight = Table(
    "flight",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("file_name", Text, nullable=False),
    Column("flt", Integer, nullable=False),
    Column("depdate", Date, nullable=False, index=True),
    Column("dep", Text, nullable=False),
)


async def create_tables():
    """Создание таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)
