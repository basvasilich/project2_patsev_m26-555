import json

from primitive_db.constants import ID_COLUMN, ID_DEFINITION, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

cache_result = create_cacher()


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт схему таблицы с обязательным столбцом ID."""
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    if not table_name.isidentifier() or not columns:
        raise ValueError("Укажите имя таблицы и её столбцы.")
    schema = [ID_DEFINITION]
    names = set()
    for column in columns:
        parts = column.split(":")
        if len(parts) != 2:
            raise ValueError(f"Некорректный столбец: {column}")
        name, data_type = parts
        if not name.isidentifier() or data_type not in VALID_TYPES or name in names:
            raise ValueError(f"Некорректный столбец: {column}")
        names.add(name)
        if name == ID_COLUMN:
            if column != ID_DEFINITION:
                raise ValueError("Столбец ID должен иметь тип int.")
        else:
            schema.append(column)
    return {**metadata, table_name: schema}


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет схему существующей таблицы."""
    if table_name not in metadata:
        raise KeyError(table_name)
    return {name: columns for name, columns in metadata.items() if name != table_name}


def validate_clause(metadata, table_name, clause, allow_id=True):
    """Проверяет наличие столбцов и точное соответствие типов."""
    schema = dict(column.split(":") for column in metadata[table_name])
    for column, value in clause.items():
        if column not in schema:
            raise KeyError(column)
        if not allow_id and column == ID_COLUMN:
            raise ValueError("Нельзя изменять ID записи.")
        if type(value) is not VALID_TYPES[schema[column]]:
            raise ValueError(f"Столбец {column} должен иметь тип {schema[column]}.")


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """Добавляет запись с новым ID без изменения исходного списка."""
    columns = [column.split(":")[0] for column in metadata[table_name]][1:]
    if len(values) != len(columns):
        raise ValueError(f"Ожидается {len(columns)} значений, получено {len(values)}.")
    row = dict(zip(columns, values))
    validate_clause(metadata, table_name, row)
    row = {
        ID_COLUMN: max((item[ID_COLUMN] for item in table_data), default=0) + 1,
        **row,
    }
    return [*table_data, row]


def matches(row, where_clause):
    """Проверяет совпадение записи с фильтром."""
    return all(row[column] == value for column, value in (where_clause or {}).items())


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает копии записей, соответствующих условию."""
    key = (
        json.dumps(table_data, sort_keys=True),
        json.dumps(where_clause, sort_keys=True),
    )
    rows = cache_result(
        key, lambda: [row.copy() for row in table_data if matches(row, where_clause)]
    )
    return [row.copy() for row in rows]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Возвращает все записи с внесёнными изменениями."""
    return [
        {**row, **set_clause} if matches(row, where_clause) else row.copy()
        for row in table_data
    ]


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Возвращает записи, не соответствующие условию удаления."""
    return [row.copy() for row in table_data if not matches(row, where_clause)]


def invalidate_cache():
    """Сбрасывает результаты выборки после изменения данных."""
    cache_result.clear()
