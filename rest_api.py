# Приложение REST API.
from fastapi import FastAPI, HTTPException
from fastapi import Path as faPath

from pathlib import Path
from pydantic import BaseModel
from typing import Union, Annotated
import uvicorn
import datetime
import re
import os

from src.sql import crud
from src.config import custom_logging

config_path = Path(f"{os.path.dirname(__file__)}/src/config/logging_config.json")


# Инициализация приложения FastApi.
def create_app() -> FastAPI:
    app = FastAPI(title="API Flying S7", debug=False)
    logger = custom_logging.CustomizeLogger.make_logger(config_path)
    app.logger = logger
    return app


app = create_app()


class ResponseStatus(BaseModel):
    status: str
    data: Union[dict, list] = None


@app.get(
    "/api/v1/getFlight/{date}",
    response_model=ResponseStatus,
    summary="Getting flight data",
)
async def get_flight(
    date: Annotated[
        str,
        faPath(
            example="2012-12-12",
            min_length=10,
            max_length=10,
            regex="\d{4}-\d\d-\d\d",
        ),
    ]
):
    """
    Получение всех записей о полетах из БД по дате.

    Args:
        date (str): обязательный параметр формата "ГГГГ-ММ-ДД"

    Returns:
        JSON: возвращаемые данные в формате {"status": str, "data": list}

        где list - список [row1, row2, row3, ....]
        row - {
            "id": int, - 1,
            "file_name": str, -"20121129_1234_DME.csv",
            "flt": int, - 1234,
            "depdate": str, - "2012-11-29",
            "dep": str, -"DME"
        }
    """
    # Регулярное выражение для проверки аргумента date на корректность.
    regular = r"^\d{4}-\d\d-\d\d$"
    match = re.search(regular, date)
    result = match[0] if match else "incorrect string"
    if date != result:
        raise HTTPException(status_code=400, detail="Incorrect string")

    try:
        date = datetime.datetime.strptime(result, "%Y-%m-%d").date()
    except:
        raise HTTPException(status_code=400, detail="Incorrect date")

    data_flight = await crud.select_flight(date)

    # Сериализация row объектов sqlalchemy в dict.
    result = [dict(dat._mapping) for dat in data_flight]

    return {"status": "1", "data": result}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port="8000")
