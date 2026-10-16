import json
import os

from primitive_db.constants import DATA_DIR, ENCODING


def load_metadata(filepath):
    """Загружает схемы таблиц из JSON."""
    try:
        with open(filepath, encoding=ENCODING) as source:
            return json.load(source)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет схемы таблиц в JSON."""
    with open(filepath, "w", encoding=ENCODING) as target:
        json.dump(data, target, ensure_ascii=False, indent=2)


def table_path(table_name):
    """Возвращает путь файла таблицы."""
    if not table_name.isidentifier():
        raise ValueError(f"Некорректное имя таблицы: {table_name}")
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """Загружает записи таблицы, отсутствующий файл означает пустую таблицу."""
    try:
        with open(table_path(table_name), encoding=ENCODING) as source:
            return json.load(source)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы."""
    filepath = table_path(table_name)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(filepath, "w", encoding=ENCODING) as target:
        json.dump(data, target, ensure_ascii=False, indent=2)


def remove_table_data(table_name):
    """Удаляет файл таблицы, если он существует."""
    filepath = table_path(table_name)
    if os.path.exists(filepath):
        os.remove(filepath)
