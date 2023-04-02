# Подключение к БД.

from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine
import os

abspath_sql = os.path.dirname(__file__)
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{abspath_sql}/DB.sqlite"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)
