from backend.memory import (
    Tables,
    create_table,
    create_item,
    select_item,
    update_item,
    delete_item
)

CURRENT_TABLE: str | None = None

# Меню

def _print_menu() -> None:
    print("\n=== База данных ===")

    print("Текущая таблица:", CURRENT_TABLE or "(не выбрана)")

    print("\n1. Создать таблицу")
    print("2. Выбрать таблицу")
    print("3. Добавить запись")
    print("4. Показать все записи")
    print("5. Найти записи по фильтру")
    print("6. Обновить запись")
    print("7. Удалить запись")
    print("8. Показать список таблиц")
    print("0. Выход")

# Таблицы

def _require_table() -> str:
    if CURRENT_TABLE is None:
        raise RuntimeError("Таблица не выбрана")
    return CURRENT_TABLE



def _read_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Ошибка: введите целое число.")


def _read_optional_int(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: число или пусто.")




def _create_table() -> None:
    name = input("Имя таблицы: ").strip()

    try:
        create_table(name)
        print(f"Таблица '{name}' создана")

    except ValueError as e:
        print("Ошибка:", e)


def _select_table() -> None:
    global CURRENT_TABLE

    if not Tables:
        print("Таблиц ещё нет")
        return

    print("\nДоступные таблицы:")
    for name in Tables:
        print("-", name)

    name = input("\nВведите имя таблицы: ").strip()

    if name not in Tables:
        print("Такой таблицы нет")
        return

    CURRENT_TABLE = name
    print(f"Выбрана таблица: {CURRENT_TABLE}")


def _show_tables() -> None:
    if not Tables:
        print("Таблиц ещё нет")
        return

    print("\nСписок таблиц:")
    for name in Tables:
        print("-", name)


# Добавление записи

def _add_item() -> None:
    try:
        table = _require_table()
    except RuntimeError as e:
        print(e)
        return

    print("\nДобавление записи")

    item_id = _read_int("id: ")
    name = input("name: ").strip()
    sector = input("sector: ").strip()
    line = _read_int("line: ")
    storey = _read_int("storey: ")

    try:
        record = create_item(
            table,
            item_id,
            name,
            sector,
            line,
            storey
        )
        print("Добавлено:", record)

    except Exception as e:
        print("Ошибка:", e)

# Вывод записи

def _print_records(records) -> None:
    if not records:
        print("Пусто")
        return

    for r in records:
        print(
            f"ID:{r[0]} | Наименование: {r[1]} | Сектор: {r[2]} | "
            f"Ряд: {r[3]} | Полка: {r[4]}"
        )

# Вывод всех записей

def _show_all() -> None:
    try:
        table = _require_table()
    except RuntimeError as e:
        print(e)
        return

    print("\nВсе записи")
    _print_records(select_item(table))


def _find() -> None:
    try:
        table = _require_table()
    except RuntimeError as e:
        print(e)
        return

    print("\nФильтр поиска")

    item_id = _read_optional_int("id: ")
    name = input("name: ").strip() or None
    sector = input("sector: ").strip() or None
    line = _read_optional_int("line: ")
    storey = _read_optional_int("storey: ")

    result = select_item(
        table,
        item_id=item_id,
        name=name,
        sector=sector,
        line=line,
        storey=storey
    )

    _print_records(result)

# Обновление записи

def _update_item() -> None:

    try:
        table = _require_table()
    except RuntimeError as e:
        print(e)
        return

    item_id = _read_int("ID записи для обновления: ")

    print("Оставьте поле пустым, чтобы не менять")

    name = input("name: ").strip() or None
    sector = input("sector: ").strip() or None
    line = _read_optional_int("line: ")
    storey = _read_optional_int("storey: ")

    try:
        updated = update_item(
            table,
            item_id,
            name,
            sector,
            line,
            storey
        )

        print("Обновлено:", updated)

    except Exception as e:
        print("Ошибка:", e)

# Удаление записи

def _delete_item() -> None:

    try:
        table = _require_table()
    except RuntimeError as e:
        print(e)
        return

    item_id = _read_int("ID записи для удаления: ")

    try:
        delete_item(table, item_id)
        print(f"Запись {item_id} удалена")

    except Exception as e:
        print("Ошибка:", e)





def run() -> None:

    global CURRENT_TABLE

    print("Запуск системы...")

    if not Tables:
        print("⚠ Таблиц ещё нет. Создайте первую таблицу.")

    while True:
        _print_menu()
        cmd = input(">>> ").strip()

        if cmd == "1":
            _create_table()

        elif cmd == "2":
            _select_table()

        elif cmd == "3":
            _add_item()

        elif cmd == "4":
            _show_all()

        elif cmd == "5":
            _find()

        elif cmd == "6":
            _show_tables()

        elif cmd == "0":
            print("Выход")
            break

        else:
            print("Неизвестная команда")