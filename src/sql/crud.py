# Функции взаимодействия с таблицами БД.

from sqlalchemy import (
    and_,
    or_,
)
from .models import *


async def insert_flight(name_file: str, flt: int, depdate: Date, dep: str):
    async with engine.begin() as conn:
        ins = flight.insert().values(
            file_name=name_file, flt=flt, depdate=depdate, dep=dep
        )
        await conn.execute(ins)


async def select_flight(date: Date):
    async with engine.begin() as conn:
        sel = flight.select().where(flight.c.depdate == date)
        data = await conn.execute(sel)
        result = data.fetchall()
        return result
        # return [dict(res) for res in result]
