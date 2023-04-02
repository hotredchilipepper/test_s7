# Тесты.
import pytest
import datetime
import shutil
import json
import os
from src.funcs.func import (
    search_files,
    parser_filename,
    parser_files,
    transfer_file,
    save_json,
    save_bd,
)

path_tests = os.path.dirname(__file__)

list_namefolders = ["In", "Out", "Ok", "Err"]

PATH_TEST = f"{path_tests}/src/tests/"

# Создание тестовых папок
for name in list_namefolders:
    os.mkdir(f"{PATH_TEST}{name}")

# Переменные путей к рабочим тестовым папкам
PATH_TEST_IN = f"{path_tests}/src/tests/In"
PATH_TEST_OK = f"{path_tests}/src/tests/Ok"
PATH_TEST_OUT = f"{path_tests}/src/tests/Out"
PATH_TEST_ERR = f"{path_tests}/src/tests/Err"
PATH_TEST_BAD = f"{path_tests}/src/tests/Empty"

list_name_file = [
    "20121129_1111_DME.csv",
    "20121129_1234_DME.csv",
    "20121129_1234_DME.txt",
    "20121129_1234_OVB.csv",
    "testfile.xls",
]


def test_create_files():
    """Создание файлов для тестирования"""
    row = (
        "num;surname;firstname;bdate\n1;IVANOV;IVAN;11NOV73\n"
        "2;PETROV;ALEXANDER;13JUL79\n3;BOSHIROV;RUSLAN;12APR78\n"
    )
    for filename in list_name_file:
        with open(f"{PATH_TEST_IN}/{filename}", "a") as file:
            file.write(row)
    filename_out = "20221211_3333_KGD.csv"
    row2 = "num;surname;firstname;bdate\n1;IVANOV;IVAN;11NOV73\n"
    with open(f"{PATH_TEST_OUT}/{filename_out}", "a") as f:
        f.write(row2)


######################################## TEST test_search_files()#######################################################################
@pytest.mark.parametrize(
    ("path", "ext", "result"),
    [
        (PATH_TEST_IN, ".txt", ["20121129_1234_DME.txt"]),
        (PATH_TEST_IN, ".xlsx", []),
        (
            PATH_TEST_IN,
            ".csv",
            ["20121129_1111_DME.csv", "20121129_1234_DME.csv", "20121129_1234_OVB.csv"],
        ),
        (PATH_TEST_IN, "asd", []),
        (PATH_TEST_IN, 10, []),
        (PATH_TEST_IN, None, []),
        (
            PATH_TEST_IN,
            "",
            [
                "20121129_1111_DME.csv",
                "20121129_1234_DME.csv",
                "20121129_1234_DME.txt",
                "20121129_1234_OVB.csv",
                "testfile.xls",
            ],
        ),
    ],
)
def test_search_files(path: str, ext: str, result: list):
    """Тест функции search_files()

    Args:
        path (str): путь к папке в которой находятся файл/файлы
        ext (str): расширение файла/файлов
        result (list): каким должен быть результат
    """
    assert search_files(path, ext) == result


def test_raises_search_files():
    with pytest.raises(AssertionError):
        search_files()


@pytest.mark.xfail()
def test_raises_search_files():
    """Тестирование на вызов исключения"""
    assert search_files(PATH_TEST_BAD, ".xls")


######################################## TEST parser_filename()#########################################################################
@pytest.mark.parametrize(
    ("filename", "result"),
    [
        (
            "20121129_1111_DME.csv",
            (datetime.datetime.strptime("20121129", "%Y%m%d").date(), "1111", "DME"),
        ),
        (
            "20110501_2222_OVB.csv",
            (datetime.datetime.strptime("20110501", "%Y%m%d").date(), "2222", "OVB"),
        ),
        (
            "20251129_3333_KGD.csv",
            (datetime.datetime.strptime("20251129", "%Y%m%d").date(), "3333", "KGD"),
        ),
        (
            "20251129_3333_KGD",
            (datetime.datetime.strptime("20251129", "%Y%m%d").date(), "3333", "KGD"),
        ),
    ],
)
def test_parser_filename(filename: str, result: tuple):
    """Тестирование функции parser_filename()

    Args:
        filename (str): имена файлов
        result (tuple): каким должен быть результат
    """
    assert parser_filename(filename) == result


def test_raises_parser_filename():
    with pytest.raises(AssertionError):
        parser_filename()


@pytest.mark.parametrize(
    ("filename"),
    [
        ("202511293333_KGD.csv"),
        ("1234.csv"),
        ("20251129_3333_KGD"),
        ("99999999_3333_KGD.csv"),
        (".csv"),
        (1234),
        (None),
        ("20251129__3333__KGD.csv"),
        ("20251129/3333/KGD.csv"),
        ("20226629_3333_KGD.csv"),
        ("20221248_3333_KGD.csv"),
    ],
)
@pytest.mark.xfail()
def test_raises_parser_filename(filename):
    """Тестирование на вызов исключения

    Args:
        filename (_type_): имена файлов неправильного формата или типа
    """
    assert parser_filename(filename)


######################################## TEST parser_files()############################################################################
@pytest.mark.parametrize(
    ("path", "filename", "result"),
    [
        (
            PATH_TEST_OUT,
            "20221211_3333_KGD.csv",
            {
                "flt": 3333,
                "date": "2022-12-11",
                "dep": "KGD",
                "prl": [
                    {
                        "num": 1,
                        "surname": "IVANOV",
                        "firstname": "IVAN",
                        "bdate": "1973-11-11",
                    }
                ],
            },
        ),
    ],
)
def test_parser_files(path: str, filename: str, result: dict):
    """Тестирование функции parser_files()

    Args:
        path (str): путь к папки где находится файл
        filename (str): имя файла для парсинга
        result (dict): каким должен быть результат
    """
    data_dict = parser_files(path, filename)
    assert type(data_dict) == dict
    assert data_dict["flt"] == result["flt"]
    assert data_dict["date"] == result["date"]
    assert data_dict["dep"] == result["dep"]
    assert data_dict["prl"] == result["prl"]


######################################## TEST transfer_file()###########################################################################
@pytest.mark.parametrize(
    ("path_dir_from", "path_dir_to", "filename"),
    [
        (PATH_TEST_IN, PATH_TEST_OUT, "testfile.xls"),
        (PATH_TEST_OUT, PATH_TEST_IN, "testfile.xls"),
        (PATH_TEST_IN, PATH_TEST_OK, "testfile.xls"),
        (PATH_TEST_OK, PATH_TEST_IN, "testfile.xls"),
        (PATH_TEST_IN, PATH_TEST_ERR, "testfile.xls"),
        (PATH_TEST_ERR, PATH_TEST_IN, "testfile.xls"),
    ],
)
def test_transfer_file(path_dir_from: str, path_dir_to: str, filename: str):
    """Тестирование функции transfer_file()

    Args:
        path_dir_from (str): путь откуда переносим файл
        path_dir_to (str): путь куда переносим файл
        filename (str): имя переносимого файла
    """
    transfer_file(path_dir_from, path_dir_to, filename)
    assert os.path.exists(f"{path_dir_to}/{filename}")


def test_raises_transfer_file():
    with pytest.raises(AssertionError):
        transfer_file()


@pytest.mark.parametrize(
    ("path_dir_from", "path_dir_to", "filename"),
    [
        (PATH_TEST_BAD, PATH_TEST_OUT, "testfile.xls"),
        (PATH_TEST_OUT, PATH_TEST_BAD, "testfile.xls"),
        ("", PATH_TEST_OK, "testfile.xls"),
        (11111, "", "testfile.xls"),
        (None, PATH_TEST_ERR, "testbad.xls"),
        (PATH_TEST_ERR, PATH_TEST_IN, "123"),
        (PATH_TEST_ERR, PATH_TEST_IN, 123),
        (PATH_TEST_ERR, PATH_TEST_IN, None),
    ],
)
@pytest.mark.xfail()
def test_raises_transfer_file(path_dir_from, path_dir_to, filename):
    """Тестирование на вызов исключения

    Args:
        path_dir_from (Any): путь откуда переносим файл
        path_dir_to (Any): путь куда переносим файл
        filename (Any): имя переносимого файла
    """
    assert transfer_file(path_dir_from, path_dir_to, filename)


######################################## TEST save_json()###############################################################################


@pytest.mark.parametrize(
    ("path_dir", "filename", "data"),
    [
        (PATH_TEST_OUT, "20110501_2222_OVB.csv", {"1": "ok"}),
        (PATH_TEST_IN, "20110501_1111_KGD.csv", {"1": "ok"}),
        (PATH_TEST_ERR, "20121212_2222_OVB.csv", {"1": "ok"}),
        (PATH_TEST_OK, "20111111_3333_KGD.csv", {"1": "ok"}),
        (PATH_TEST_OUT, "20110522_2224_OVB.csv", {"1": "ok"}),
    ],
)
@pytest.mark.asyncio
async def test_save_json(path_dir: str, filename: str, data: dict):
    """Тестирование функции save_json()

    Args:
        path_dir (str): путь куда сохранить файл json
        filename (str): название исходного файла
        data (dict): данные ввиде словаря
    """
    await save_json(path_dir, filename, data)
    new_file_name = filename.split(".")[0] + ".json"
    full_path = f"{path_dir}/{new_file_name}"
    assert os.path.exists(full_path)
    with open(full_path) as f:
        templates = json.load(f)
    assert templates == data


########################################################################################################################################
# Удаление тестовых директорий и файлов внутри
def test_delete_folders_with_files():
    for name in list_namefolders:
        shutil.rmtree(PATH_TEST + name)


# TODO Создать тестовую базу данных и аписать тесты на функции работающими с БД.

# TODO Написать тесты на метод REST API "/api/v1/getFlight/{date}".
