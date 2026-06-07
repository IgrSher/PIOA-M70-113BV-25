from .backend.memory import (
    Tables,
    create_table,
    create_item,
    select_item,
    update_item,
    delete_item,
    get_schema,
    get_columns,
)

CURRENT_TABLE: str | None = None


def _print_menu() -> None:
    print("\n=== База данных ===")
    print(
        "Текущая таблица:",
        CURRENT_TABLE or "(не выбрана)"
    )

    print("\n1. Создать таблицу")
    print("2. Выбрать таблицу")
    print("3. Добавить запись")
    print("4. Показать все записи")
    print("5. Найти записи")
    print("6. Обновить запись")
    print("7. Удалить запись")
    print("8. Показать список таблиц")
    print("0. Выход")


def _require_table() -> str:

    if CURRENT_TABLE is None:
        raise RuntimeError(
            "Таблица не выбрана"
        )

    return CURRENT_TABLE


def _read_int(
    prompt: str
) -> int:

    while True:

        try:
            return int(
                input(prompt).strip()
            )

        except ValueError:
            print(
                "Введите целое число"
            )


def _show_tables() -> None:

    if not Tables:
        print(
            "Таблиц ещё нет"
        )
        return

    print("\nТаблицы:")

    for table_name in Tables:
        print(
            "-",
            table_name
        )


def _create_table() -> None:

    table_name = input(
        "Имя таблицы: "
    ).strip()

    columns_count = _read_int(
        "Количество столбцов "
        "(без id): "
    )

    columns = []

    for i in range(columns_count):

        print(
            f"\nСтолбец №{i + 1}"
        )

        column_name = input(
            "Название: "
        ).strip()

        while True:

            column_type = input(
                "Тип (int/str): "
            ).strip().lower()

            if column_type in (
                "int",
                "str"
            ):
                break

            print(
                "Допустимые типы:"
                " int, str"
            )

        columns.append(
            (
                column_name,
                column_type
            )
        )

    try:

        create_table(
            table_name,
            columns
        )

        print(
            f"Таблица "
            f"'{table_name}' "
            f"создана"
        )

    except ValueError as e:

        print(
            "Ошибка:",
            e
        )


def _select_table() -> None:

    global CURRENT_TABLE

    if not Tables:

        print(
            "Таблиц ещё нет"
        )

        return

    print(
        "\nДоступные таблицы:"
    )

    for name in Tables:
        print(
            "-",
            name
        )

    table_name = input(
        "\nВведите имя таблицы: "
    ).strip()

    if table_name not in Tables:

        print(
            "Такой таблицы нет"
        )

        return

    CURRENT_TABLE = table_name

    print(
        f"Выбрана таблица: "
        f"{CURRENT_TABLE}"
    )


def _add_item() -> None:

    try:

        table_name = _require_table()

    except RuntimeError as e:

        print(e)

        return

    schema = get_schema(
        table_name
    )

    record = {}

    print(
        "\nДобавление записи"
    )

    for field_name, field_type in schema.items():

        if field_type is int:

            value = _read_int(
                f"{field_name}: "
            )

        else:

            value = input(
                f"{field_name}: "
            ).strip()

        record[field_name] = value

    try:

        created = create_item(
            table_name,
            record
        )

        print(
            "\nДобавлено:"
        )

        print(created)

    except ValueError as e:

        print(
            "Ошибка:",
            e
        )


def _print_records(
    records: list[dict]
) -> None:

    if not records:

        print("Пусто")

        return

    for record in records:

        parts = []

        for key, value in record.items():

            parts.append(
                f"{key}: {value}"
            )

        print(
            " | ".join(parts)
        )


def _show_all() -> None:

    try:

        table_name = _require_table()

    except RuntimeError as e:

        print(e)

        return

    records = select_item(
        table_name
    )

    _print_records(
        records
    )


def _find() -> None:

    try:

        table_name = _require_table()

    except RuntimeError as e:

        print(e)

        return

    schema = get_schema(
        table_name
    )

    print(
        "\nДоступные поля:"
    )

    for field in schema:
        print("-", field)

    field_name = input(
        "\nПоле: "
    ).strip()

    if field_name not in schema:

        print(
            "Такого поля нет"
        )

        return

    field_type = schema[
        field_name
    ]

    if field_type is int:

        value = _read_int(
            "Значение: "
        )

    else:

        value = input(
            "Значение: "
        ).strip()

    result = select_item(
        table_name,
        {
            field_name: value
        }
    )

    _print_records(
        result
    )


def _update_item() -> None:

    try:

        table_name = _require_table()

    except RuntimeError as e:

        print(e)

        return

    schema = get_schema(
        table_name
    )

    item_id = _read_int(
        "ID записи: "
    )

    updates = {}

    print(
        "\nОставьте поле "
        "пустым чтобы "
        "не изменять его"
    )

    for field_name, field_type in schema.items():

        if field_name == "id":
            continue

        raw = input(
            f"{field_name}: "
        ).strip()

        if raw == "":
            continue

        if field_type is int:

            try:
                updates[field_name] = int(
                    raw
                )

            except ValueError:

                print(
                    f"{field_name} "
                    f"должен быть int"
                )

                return

        else:

            updates[field_name] = raw

    try:

        updated = update_item(
            table_name,
            item_id,
            updates
        )

        print(
            "\nОбновлено:"
        )

        print(updated)

    except ValueError as e:

        print(
            "Ошибка:",
            e
        )


def _delete_item() -> None:

    try:

        table_name = _require_table()

    except RuntimeError as e:

        print(e)

        return

    item_id = _read_int(
        "ID записи: "
    )

    try:

        delete_item(
            table_name,
            item_id
        )

        print(
            "Запись удалена"
        )

    except ValueError as e:

        print(
            "Ошибка:",
            e
        )


def run() -> None:

    print(
        "Запуск системы..."
    )

    while True:

        _print_menu()

        command = input(
            ">>> "
        ).strip()

        if command == "1":

            _create_table()

        elif command == "2":

            _select_table()

        elif command == "3":

            _add_item()

        elif command == "4":

            _show_all()

        elif command == "5":

            _find()

        elif command == "6":

            _update_item()

        elif command == "7":

            _delete_item()

        elif command == "8":

            _show_tables()

        elif command == "0":

            print(
                "Выход"
            )

            break

        else:

            print(
                "Неизвестная команда"
            )