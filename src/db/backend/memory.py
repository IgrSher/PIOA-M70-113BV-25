
TYPE_MAP = {
    "int": int,
    "str": str,
}

Tables: dict[str, dict] = {}

ID_LENGTH = 3


def create_table(
    table_name: str,
    columns: list[tuple[str, str]]
) -> None:

    table_name = table_name.strip()

    if not table_name:
        raise ValueError(
            "Имя таблицы не может быть пустым"
        )

    if table_name in Tables:
        raise ValueError(
            f"Таблица '{table_name}' уже существует"
        )

    schema = {
        "id": int
    }

    for column_name, column_type in columns:

        column_name = column_name.strip()
        column_type = column_type.strip().lower()

        if not column_name:
            raise ValueError(
                "Имя столбца не может быть пустым"
            )

        if column_name == "id":
            raise ValueError(
                "Столбец 'id' создаётся автоматически"
            )

        if column_name in schema:
            raise ValueError(
                f"Столбец '{column_name}' уже существует"
            )

        if column_type not in TYPE_MAP:
            raise ValueError(
                "Допустимые типы: int, str"
            )

        schema[column_name] = TYPE_MAP[column_type]

    Tables[table_name] = {
        "schema": schema,
        "rows": []
    }


def _get_table(table_name: str) -> dict:

    if table_name not in Tables:
        raise ValueError(
            f"Таблица '{table_name}' не существует"
        )

    return Tables[table_name]


def _validate_record(
    schema: dict,
    record: dict
) -> None:

    if "id" not in record:
        raise ValueError("Отсутствует ID")

    item_id = record["id"]

    if not isinstance(item_id, int):
        raise ValueError(
            "ID должен быть целым числом"
        )

    if len(str(abs(item_id))) != ID_LENGTH:
        raise ValueError(
            "ID должен содержать 3 цифры"
        )

    for field_name, field_type in schema.items():

        if field_name not in record:
            raise ValueError(
                f"Поле '{field_name}' отсутствует"
            )

        value = record[field_name]

        if field_type is int:

            if not isinstance(value, int):
                raise ValueError(
                    f"Поле '{field_name}' "
                    f"должно быть int"
                )

        elif field_type is str:

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                raise ValueError(
                    f"Поле '{field_name}' "
                    f"должно быть непустой строкой"
                )


def create_item(
    table_name: str,
    data: dict
) -> dict:

    table = _get_table(table_name)

    schema = table["schema"]
    rows = table["rows"]

    _validate_record(schema, data)

    for row in rows:

        if row["id"] == data["id"]:
            raise ValueError(
                f"Запись с ID "
                f"{data['id']} уже существует"
            )

    rows.append(data.copy())

    return data.copy()


def select_item(
    table_name: str,
    filters: dict | None = None
) -> list[dict]:

    table = _get_table(table_name)

    rows = table["rows"]

    if not filters:
        return [row.copy() for row in rows]

    result = []

    for row in rows:

        matched = True

        for field, value in filters.items():

            if row.get(field) != value:
                matched = False
                break

        if matched:
            result.append(row.copy())

    return result


def update_item(
    table_name: str,
    item_id: int,
    updates: dict
) -> dict:

    table = _get_table(table_name)

    schema = table["schema"]
    rows = table["rows"]

    for row in rows:

        if row["id"] == item_id:

            updated = row.copy()

            for key, value in updates.items():

                if key == "id":
                    continue

                if key not in schema:
                    raise ValueError(
                        f"Поле '{key}' "
                        f"не существует"
                    )

                updated[key] = value

            _validate_record(
                schema,
                updated
            )

            row.clear()
            row.update(updated)

            return updated.copy()

    raise ValueError(
        f"Запись с ID {item_id} не найдена"
    )


def delete_item(
    table_name: str,
    item_id: int
) -> None:

    table = _get_table(table_name)

    rows = table["rows"]

    for index, row in enumerate(rows):

        if row["id"] == item_id:

            del rows[index]
            return

    raise ValueError(
        f"Запись с ID {item_id} не найдена"
    )


def get_schema(
    table_name: str
) -> dict[str, type]:

    table = _get_table(table_name)

    return table["schema"].copy()


def get_columns(
    table_name: str
) -> list[str]:

    table = _get_table(table_name)

    return list(
        table["schema"].keys()
    )