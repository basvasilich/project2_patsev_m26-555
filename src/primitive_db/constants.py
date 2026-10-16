META_FILE = "db_meta.json"
DATA_DIR = "data"
ENCODING = "utf-8"
VALID_TYPES = {"int": int, "str": str, "bool": bool}
ID_COLUMN = "ID"
ID_DEFINITION = "ID:int"
PUNCTUATION = "(),="
BOOL_VALUES = {"true": True, "false": False}
HELP = """***База данных***
create_table <таблица> <столбец:тип> ... — создать таблицу
list_tables — список таблиц
drop_table <таблица> — удалить таблицу
insert into <таблица> values (<значение>, ...) — добавить запись
select from <таблица> [where <столбец> = <значение>] — выбрать записи
update <таблица> set <столбец> = <значение> where <столбец> = <значение>
delete from <таблица> where <столбец> = <значение> — удалить записи
info <таблица> — схема и количество записей
help — справка
exit — выход
"""
