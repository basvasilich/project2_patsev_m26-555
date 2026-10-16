# Примитивная база данных

ДЗ №2 по Python, Пацев Вадим, М26-555
Консольная БД с таблицами в JSON, CRUD, проверкой типов, декораторами и кэшем

## Установка и запуск

Нужны Python 3.12+ и [uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
git clone https://github.com/basvasilich/project2_patsev_m26-555.git
cd project2_patsev_m26-555
uv sync --locked
uv run database
```

Также доступны `make install` и `make run`

## Команды

```text
create_table users name:str age:int is_active:bool
list_tables
insert into users values ("Sergei", 28, true)
select from users
select from users where age = 28
update users set age = 29 where name = "Sergei"
delete from users where ID = 1
y
info users
drop_table users
y
help
exit
```

Типы — `int`, `str`, `bool`. Строки вводятся в кавычках, ID создаётся автоматически
Схемы хранятся в `db_meta.json`, записи — в `data/<таблица>.json`
Удаление требует `y`, другой ответ отменяет операцию. Ошибки не прерывают сеанс
`insert` и `select` выводят время выполнения. После изменений кэш выборок очищается

## Проверка и сборка

```bash
uv run ruff check .
uv build
uvx twine check dist/*
```

## Демонстрация

[![asciinema](https://asciinema.org/a/m0JqT4YZ895a28r1.svg)](https://asciinema.org/a/m0JqT4YZ895a28r1)

[Локальная копия](docs/demo.cast). Без привязки к аккаунту запись хранится 7 дней
