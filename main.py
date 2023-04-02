# Парсинг входящих файлов и перезапись в другой каталог, и запись в базу данных.

import asyncio
import logging
import os

from src.sql.models import create_tables
from src.funcs.func import search_files, parser_files, save_json, save_bd, transfer_file

import time


async def main():
    # Основной цикл работы программы.
    while True:
        # Получение файла/файлов для обработки
        start_time = time.time()
        list_files = search_files(PATH_DIR_IN, ".csv")
        if list_files:
            logging.info(f"Got a list of files to process: {list_files}")
        for file in list_files:
            try:
                # Получение данных из файла
                data_parser = parser_files(
                    PATH_DIR_IN,
                    file,
                )

                # Реализация с помощью asyncio "параллельной" обработки двух задач,
                # Сохранения файла и записи в таблицу.
                task_save_json = asyncio.create_task(
                    save_json(PATH_DIR_OUT, file, data_parser)
                )
                task_save_bd = asyncio.create_task(save_bd(file))

                await task_save_json
                await task_save_bd
                # Перемещение файла после успешной обработки в директорию "Ok".
                transfer_file(PATH_DIR_IN, PATH_DIR_OK, file)
            except Exception:
                logging.error(
                    f"An error occurred while processing the file: {file}",
                    exc_info=True,
                )
                # Перемещение файла с ошибкой в директорию "Err".
                transfer_file(PATH_DIR_IN, PATH_DIR_ERR, file)
        end_time = time.time()
        # Получение дрейфа по времени выполнения основной части программы,
        # если дреф по времени получается отрицательным то следующая итерация запускается сразу.
        drift_time = round(TIME_SEC - (end_time - start_time), 4)

        if drift_time > 0:
            await asyncio.sleep(drift_time)


if __name__ == "__main__":
    # Абсолютные пути к рабочим(результирующим) директориям.

    # Получаем строку, содержащую путь к рабочей директории:
    abspath_proj = os.path.dirname(__file__)
    PATH_DIR_IN = f"{abspath_proj}/src/folders/In"
    PATH_DIR_OK = f"{abspath_proj}/src/folders/Ok"
    PATH_DIR_OUT = f"{abspath_proj}/src/folders/Out"
    PATH_DIR_ERR = f"{abspath_proj}/src/folders/Err"

    # Создание рабочих каталогов
    list_dir = ["folders", "logs", "tests"]
    for name in list_dir:
        full_path = f"{abspath_proj}/src/{name}"
        if os.path.exists(full_path) != True:
            os.mkdir(full_path)

    # Создание подкаталогов в folders
    list_folders_dirs = ["In", "Out", "Ok", "Err"]
    for name in list_folders_dirs:
        full_path = f"{abspath_proj}/src/folders/{name}"
        if os.path.exists(full_path) != True:
            os.mkdir(full_path)

    TIME_SEC = 60
    PATH_LOGS = f"{abspath_proj}/src/logs/main.log"

    logging.basicConfig(
        level=logging.INFO,
        filename=PATH_LOGS,
        filemode="a",
        format="%(asctime)s %(levelname)s %(message)s",
    )

    asyncio.run(create_tables())
    asyncio.run(main())
