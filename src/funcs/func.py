import pandas as pd
import datetime

import shutil
import logging
import json
import os

from src.sql import crud


abs_path = os.path.dirname(__file__)

PATH_LOGS = f"{abs_path}/logs/main.log"


logging.basicConfig(
    level=logging.INFO,
    filename=PATH_LOGS,
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s",
)


def search_files(path_dir: str, file_ext: str) -> list:
    """Получения списка файлов из заданной директории.

    Args:
        path_dir (str): путь к папке в которой будет поиск
        file_ext (str): расширение искомых файлов, пример ".txt"

    Returns:
        list: список файлов, полный путь + имя в заданном каталоге по расширению
    """
    file_dir = rf"{path_dir}"
    file_ext = rf"{file_ext}"
    return [_ for _ in os.listdir(file_dir) if _.endswith(file_ext)]


def parser_filename(name_file: str) -> tuple:
    """Преобразование имени файла строгого формата в данные.

    Args:
        name_file (str): имя файла, формата - 20221229_1234_DME.csv где
            <год><месяц><день>_<номер рейса>_<аэропорт вылета>.csv

    Returns:
        tuple: данные в в строгом порядке (дата, номер рейса, аэропорт вылета)
    """
    # Разбор имени файла
    date, number, flight = name_file.split(".")[0].split("_")
    date = datetime.datetime.strptime(date, "%Y%m%d").date()
    return (date, number, flight)


def parser_files(path_dir: str, name_file: str) -> dict:
    """Парсинг файла csv.

    Args:
        path_dir (str): путь к директории где находится файл
        name_file (str): имя файла

    Returns:
        dict: данные из файла преобразованные в словарь
    """
    date, number, flight = parser_filename(name_file)
    # Парсинг данных из файла
    path_file = path_dir + r"\\" + name_file
    # Преобразование данных из файла в dataframe
    df = pd.read_csv(path_file, sep=";")
    # Преобразование всех данных из колонки в строчное представление даты ISO
    df["bdate"] = df["bdate"].apply(
        lambda x: str(datetime.datetime.strptime(x, "%d%b%y").date())
    )
    passenger_list = df.to_dict("records")
    return {"flt": int(number), "date": str(date), "dep": flight, "prl": passenger_list}


def transfer_file(path_dir_from: str, path_dir_to: str, name_file: str) -> None:
    """Перемещение файла из директории в другую директорию

    Args:
        path_dir_from (str): путь где находится файл для перемещения
        path_dir_to (str): путь куда нужно переместить файл
        name_file (str): имя файла
    """
    path_file = path_dir_from + r"\\" + name_file
    # В процессе разработки столкнулся случайно с проблемой перемещения файлов
    # когда в директории куда перемещали файл, уже был файл с таким же именем,
    # решил реализовать дополнительный цикл для того чтобы записывать дублирующиеся
    # файлы с префиксом "_n" где n - кол-во файлов с одинаковым именем.
    if not os.path.exists(path_dir_to + r"\\" + name_file):
        shutil.move(path_file, path_dir_to)
        logging.info(f"File moved successfully: {path_dir_to}" + f"\{name_file}")
    else:
        counter = 1
        while True:
            new_name_file = name_file.split(".")[0] + f"_{counter}.csv"
            if not os.path.exists(path_dir_to + r"\\" + new_name_file):
                new_path_dir_to = path_dir_to + r"\\" + new_name_file
                shutil.move(path_file, new_path_dir_to)
                logging.warning(
                    f"File successfully moved with new name and path: {new_path_dir_to}"
                )
                break


async def save_json(path_dir: str, name_file: str, data: dict) -> None:
    """Запись данных в файл json.

    Args:
        path_dir (str): путь к директории для записи файла
        name_file (str): имя файла
        data (dict): словарь для сериализации в json
    """
    name_file = name_file.split(".")[0] + ".json"
    path = path_dir + r"\\" + name_file
    with open(path, "w") as outfile:
        json.dump(data, outfile, indent=4)

    logging.info(f"Successfully written file: {path}")


async def save_bd(name_file: str) -> None:
    """Запись данных в таблицу БД.

    Args:
        name_file (str): имя файла
    """
    date, number, flight = parser_filename(name_file)
    await crud.insert_flight(name_file, int(number), date, flight)

    logging.info("Created a new entry in the table <flight>")
