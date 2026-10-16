import prompt
from prettytable import PrettyTable

from primitive_db.constants import HELP, ID_COLUMN, META_FILE
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    invalidate_cache,
    matches,
    select,
    update,
    validate_clause,
)
from primitive_db.decorators import handle_db_errors
from primitive_db.parser import parse_command
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    remove_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Выводит список команд."""
    print(HELP)


def show_rows(columns, rows):
    """Выводит записи с помощью PrettyTable."""
    names = [column.split(":")[0] for column in columns]
    table = PrettyTable(names)
    for row in rows:
        table.add_row([row[name] for name in names])
    print(table)


def persist_rows(table_name, rows):
    """Сохраняет записи и очищает кэш выборки."""
    save_table_data(table_name, rows)
    invalidate_cache()


def change_rows(metadata, command, table_data):
    """Выполняет изменение данных и сообщает затронутые ID."""
    name = command["command"]
    table_name = command["table"]
    if name == "insert":
        result = insert(metadata, table_name, command["values"], table_data)
        if result is not None:
            persist_rows(table_name, result)
            print(
                f"Запись с ID={result[-1][ID_COLUMN]} успешно добавлена "
                f'в таблицу "{table_name}".'
            )
        return
    where_clause = command["where"]
    validate_clause(metadata, table_name, where_clause)
    affected_ids = [row[ID_COLUMN] for row in table_data if matches(row, where_clause)]
    if name == "update":
        validate_clause(metadata, table_name, command["set"], allow_id=False)
        result = update(table_data, command["set"], where_clause)
        action = "обновлена"
    else:
        result = delete(table_data, where_clause)
        action = "удалена"
    if result is not None:
        persist_rows(table_name, result)
        for row_id in affected_ids:
            print(f'Запись с ID={row_id} в таблице "{table_name}" успешно {action}.')
        if not affected_ids:
            print("Подходящих записей нет.")


@handle_db_errors
def execute(user_input):
    """Разбирает и выполняет одну команду."""
    command = parse_command(user_input)
    name = command["command"]
    if name == "help":
        print_help()
        return
    if name == "exit":
        return
    metadata = load_metadata(META_FILE)
    if name == "list_tables":
        for table_name in metadata:
            print(f"- {table_name}")
        return
    table_name = command["table"]
    if name == "create_table":
        result = create_table(metadata, table_name, command["columns"])
        if result is not None:
            persist_rows(table_name, [])
            save_metadata(META_FILE, result)
            print(
                f'Таблица "{table_name}" успешно создана со столбцами: '
                f"{', '.join(result[table_name])}"
            )
        return
    if table_name not in metadata:
        raise KeyError(table_name)
    if name == "drop_table":
        result = drop_table(metadata, table_name)
        if result is not None:
            remove_table_data(table_name)
            save_metadata(META_FILE, result)
            print(f'Таблица "{table_name}" успешно удалена.')
            invalidate_cache()
        return
    table_data = load_table_data(table_name)
    if name == "info":
        print(f"Таблица: {table_name}")
        print(f"Столбцы: {', '.join(metadata[table_name])}")
        print(f"Количество записей: {len(table_data)}")
    elif name == "select":
        validate_clause(metadata, table_name, command["where"] or {})
        rows = select(table_data, command["where"])
        if rows is not None:
            show_rows(metadata[table_name], rows)
    else:
        change_rows(metadata, command, table_data)


def run():
    """Запускает цикл чтения команд."""
    print_help()
    while True:
        try:
            user_input = prompt.string("Введите команду: ")
            if user_input.strip().lower() == "exit":
                break
            execute(user_input)
        except (EOFError, KeyboardInterrupt):
            print()
            break
