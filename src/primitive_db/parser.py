import json
import shlex

from primitive_db.constants import BOOL_VALUES, PUNCTUATION


def tokenize(expression):
    """Разбивает команду, сохраняя кавычки строковых значений."""
    prefix = "__quoted_value_"
    while prefix in expression:
        prefix += "_"
    literals = {}
    parts = []
    position = 0
    while position < len(expression):
        quote = expression[position]
        if quote not in "\"'":
            parts.append(quote)
            position += 1
            continue
        end = position + 1
        while end < len(expression):
            if expression[end] == "\\" and quote == '"':
                end += 2
            elif expression[end] == quote:
                break
            else:
                end += 1
        if end >= len(expression):
            raise ValueError("Незакрытые кавычки.")
        marker = f"{prefix}{len(literals)}"
        literals[marker] = expression[position : end + 1]
        parts.append(marker)
        position = end + 1
    lexer = shlex.shlex("".join(parts), posix=True, punctuation_chars=PUNCTUATION)
    lexer.whitespace_split = True
    lexer.commenters = ""
    tokens = []
    for token in lexer:
        if all(character in PUNCTUATION for character in token):
            tokens.extend(token)
        else:
            tokens.append(literals.get(token, token))
    return tokens


def parse_value(token):
    """Преобразует литерал в str, int или bool."""
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return json.loads(token) if token[0] == '"' else token[1:-1]
    if token.lower() in BOOL_VALUES:
        return BOOL_VALUES[token.lower()]
    digits = token.lstrip("+-")
    if digits and digits.isdecimal() and token[:2] not in ("++", "--", "+-", "-+"):
        return int(token)
    raise ValueError(f"Некорректное значение: {token}. Строки нужны в кавычках.")


def parse_values(expression):
    """Разбирает список значений в круглых скобках."""
    tokens = tokenize(expression) if isinstance(expression, str) else expression
    if not tokens or tokens[0] != "(" or tokens[-1] != ")":
        raise ValueError("Значения должны быть в круглых скобках.")
    tokens = tokens[1:-1]
    if not tokens:
        return []
    if len(tokens) % 2 != 1 or any(token != "," for token in tokens[1::2]):
        raise ValueError("Значения должны разделяться запятыми.")
    return [parse_value(token) for token in tokens[::2]]


def parse_set(expression):
    """Разбирает присваивания вида age = 28, name = \"Ann\"."""
    tokens = tokenize(expression) if isinstance(expression, str) else expression
    assignments = {}
    while tokens:
        if len(tokens) < 3 or tokens[1] != "=" or not tokens[0].isidentifier():
            raise ValueError("Ожидается условие <столбец> = <значение>.")
        column = tokens[0]
        if column in assignments:
            raise ValueError(f"Столбец {column} указан повторно.")
        assignments[column] = parse_value(tokens[2])
        tokens = tokens[3:]
        if tokens:
            if tokens[0] != "," or len(tokens) == 1:
                raise ValueError("Присваивания должны разделяться запятыми.")
            tokens = tokens[1:]
    if not assignments:
        raise ValueError("Укажите хотя бы одно условие.")
    return assignments


def parse_where(expression):
    """Разбирает одно условие равенства."""
    result = parse_set(expression)
    if len(result) != 1:
        raise ValueError("В where поддерживается одно условие равенства.")
    return result


def parse_command(user_input):
    """Возвращает имя команды и разобранные аргументы."""
    tokens = tokenize(user_input)
    if not tokens:
        raise ValueError("Введите команду.")
    command = tokens[0].lower()
    result = {"command": command}
    if command in ("help", "exit", "list_tables") and len(tokens) == 1:
        return result
    if command == "create_table" and len(tokens) >= 3:
        return {**result, "table": tokens[1], "columns": tokens[2:]}
    if command in ("drop_table", "info") and len(tokens) == 2:
        return {**result, "table": tokens[1]}
    if command == "insert" and len(tokens) >= 6:
        if tokens[1].lower() == "into" and tokens[3].lower() == "values":
            return {**result, "table": tokens[2], "values": parse_values(tokens[4:])}
    if command == "select" and len(tokens) >= 3 and tokens[1].lower() == "from":
        if len(tokens) == 3:
            return {**result, "table": tokens[2], "where": None}
        if tokens[3].lower() == "where":
            return {**result, "table": tokens[2], "where": parse_where(tokens[4:])}
    if command == "delete" and len(tokens) >= 7:
        if tokens[1].lower() == "from" and tokens[3].lower() == "where":
            return {**result, "table": tokens[2], "where": parse_where(tokens[4:])}
    if command == "update" and len(tokens) >= 10 and tokens[2].lower() == "set":
        positions = [
            i for i, token in enumerate(tokens[3:], 3) if token.lower() == "where"
        ]
        if len(positions) == 1:
            position = positions[0]
            return {
                **result,
                "table": tokens[1],
                "set": parse_set(tokens[3:position]),
                "where": parse_where(tokens[position + 1 :]),
            }
    known = (
        "help",
        "exit",
        "list_tables",
        "create_table",
        "drop_table",
        "info",
        "insert",
        "select",
        "delete",
        "update",
    )
    if command not in known:
        raise ValueError(f"Функции {tokens[0]} нет. Попробуйте снова.")
    raise ValueError("Некорректная команда. Введите help для справки.")
