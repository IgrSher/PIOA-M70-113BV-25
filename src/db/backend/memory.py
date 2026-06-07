
Item = tuple[int, str, str, int, int]

Tables: dict[str, list[Item]] = {}

ID_LENGTH = 2


# Cоздание таблицы

def create_table(table_name: str) -> None:
    if table_name in Tables:
        raise ValueError(f"Таблица '{table_name}' уже существует")

    Tables[table_name] = []

# Выбор таблицы

def _get_table(table_name: str) -> list[Item]:
    if table_name not in Tables:
        raise ValueError(f"Таблица '{table_name}' не существует")
    return Tables[table_name]


# Создание записи

def create_item(
    table_name: str,
    item_id: int,
    name: str,
    sector: str,
    line: int,
    storey: int
) -> Item:

    table = _get_table(table_name)

    if not isinstance(item_id, int):
        raise TypeError("ID должен быть целым числом")

    if len(str(abs(item_id))) != ID_LENGTH:
        raise ValueError("ID должен содержать 2 цифры")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Некорректное наименование")

    if not isinstance(sector, str) or not sector.strip():
        raise ValueError("Некорректный сектор")

    if not isinstance(line, int) or line < 0:
        raise ValueError("Номер ряда должен быть положительным числом")

    if not isinstance(storey, int) or storey < 0:
        raise ValueError("Номер яруса должен быть положительным числом")

    # уникальность внутри таблицы
    for item in table:
        if item[0] == item_id:
            raise ValueError(f"Запись с ID {item_id} уже существует")

    item: Item = (
        item_id,
        name.strip(),
        sector.strip(),
        line,
        storey
    )

    table.append(item)
    return item



# Чтение записей


def select_item(
    table_name: str,
    item_id: int | None = None,
    name: str | None = None,
    sector: str | None = None,
    line: int | None = None,
    storey: int | None = None
) -> list[Item]:

    table = _get_table(table_name)

    if (
        item_id is None
        and name is None
        and sector is None
        and line is None
        and storey is None
    ):
        return table.copy()

    result: list[Item] = []

    for record in table:

        if item_id is not None and record[0] != item_id:
            continue

        if name is not None and record[1] != name:
            continue

        if sector is not None and record[2] != sector:
            continue

        if line is not None and record[3] != line:
            continue

        if storey is not None and record[4] != storey:
            continue

        result.append(record)

    return result

# Обновление записей

def update_item(
    table_name: str,
    item_id: int,
    name: str | None = None,
    sector: str | None = None,
    line: int | None = None,
    storey: int | None = None
) -> Item:

    table = _get_table(table_name)

    for i, item in enumerate(table):

        if item[0] == item_id:

            updated = (
                item[0],
                name.strip() if name is not None else item[1],
                sector.strip() if sector is not None else item[2],
                line if line is not None else item[3],
                storey if storey is not None else item[4],
            )

            table[i] = updated
            return updated

    raise ValueError(f"Запись с ID {item_id} не найдена")

# Удаление записей
def delete_item(table_name: str, item_id: int) -> None:

    table = _get_table(table_name)

    for i, item in enumerate(table):

        if item[0] == item_id:
            del table[i]
            return

    raise ValueError(f"Запись с ID {item_id} не найдена")