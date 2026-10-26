from .backend.memory import MemoryDB
from .backend.errors import DatabaseError


class TUI:
    def __init__(self, db=None):
        if db is None:
            self.db = MemoryDB()
        else:
            self.db = db

        self.current_table = None

    def _print_menu(self) -> None:
        print("\n=== База данных ===")
        print(
            "Текущая таблица:",
            self.current_table or "(не выбрана)"
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

    def _require_table(self) -> str:
        if self.current_table is None:
            raise RuntimeError(
                "Таблица не выбрана"
            )

        return self.current_table

    def _read_int(
        self,
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

    def _show_tables(self) -> None:
        tables = self.db.get_tables()

        if not tables:
            print(
                "Таблиц ещё нет"
            )
            return

        print("\nТаблицы:")

        for table_name in tables:
            print("-", table_name)

    def _create_table(self) -> None:
        table_name = input(
            "Имя таблицы: "
        ).strip()

        columns_count = self._read_int(
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
                    "Допустимые типы: "
                    "int, str"
                )

            columns.append(
                (
                    column_name,
                    column_type
                )
            )

        try:

            self.db.create_table(table_name, columns)

            print(
                f"Таблица "
                f"'{table_name}' "
                f"создана"
            )

        except DatabaseError as e:

            print(
                "Ошибка:",
                e
            )

    def _select_table(self) -> None:
        tables = self.db.get_tables()

        if not tables:

            print(
                "Таблиц ещё нет"
            )

            return

        print(
            "\nДоступные таблицы:"
        )

        for name in tables:
            print("-", name)

        table_name = input(
            "\nВведите имя таблицы: "
        ).strip()

        if table_name not in tables:

            print(
                "Такой таблицы нет"
            )

            return

        self.current_table = table_name

        print(
            f"Выбрана таблица: "
            f"{self.current_table}"
        )

    def _add_item(self) -> None:

        try:

            table_name = (
                self._require_table()
            )

        except RuntimeError as e:

            print(e)

            return

        schema = self.db.get_schema(table_name)

        record = {}

        print(
            "\nДобавление записи"
        )

        for field_name, field_type in schema.items():

            if field_type is int:

                value = self._read_int(
                    f"{field_name}: "
                )

            else:

                value = input(
                    f"{field_name}: "
                ).strip()

            record[field_name] = value

        try:

            created = self.db.create_item(table_name, record)

            print(
                "\nДобавлено:"
            )

            print(created)

        except DatabaseError as e:

            print(
                "Ошибка:",
                e
            )

    def _print_records(
        self,
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

    def _show_all(self) -> None:

        try:

            table_name = (
                self._require_table()
            )

        except RuntimeError as e:

            print(e)

            return

        records = self.db.select_item(table_name)

        self._print_records(
            records
        )

    def _find(self) -> None:

        try:

            table_name = (
                self._require_table()
            )

        except RuntimeError as e:

            print(e)

            return

        schema = self.db.get_schema(table_name)

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

            value = self._read_int(
                "Значение: "
            )

        else:

            value = input(
                "Значение: "
            ).strip()

        result = self.db.select_item(table_name)

        self._print_records(
            result
        )

    def _update_item(self) -> None:

        try:

            table_name = (
                self._require_table()
            )

        except RuntimeError as e:

            print(e)

            return

        schema = self.db.get_schema(table_name)

        item_id = self._read_int(
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

                    updates[
                        field_name
                    ] = int(raw)

                except ValueError:

                    print(
                        f"{field_name} "
                        f"должен быть int"
                    )

                    return

            else:

                updates[
                    field_name
                ] = raw

        try:

            updated = self.db.update_item(table_name, item_id, updates)

            print(
                "\nОбновлено:"
            )

            print(updated)

        except DatabaseError as e:

            print(
                "Ошибка:",
                e
            )

    def _delete_item(self) -> None:

        try:

            table_name = (
                self._require_table()
            )

        except RuntimeError as e:

            print(e)

            return

        item_id = self._read_int(
            "ID записи: "
        )

        try:

            self.db.delete_item(table_name, item_id)

            print(
                "Запись удалена"
            )

        except DatabaseError as e:

            print(
                "Ошибка:",
                e
            )

    def run(self) -> None:

        print(
            "Запуск системы..."
        )

        while True:

            self._print_menu()

            command = input(
                ">>> "
            ).strip()

            if command == "1":

                self._create_table()

            elif command == "2":

                self._select_table()

            elif command == "3":

                self._add_item()

            elif command == "4":

                self._show_all()

            elif command == "5":

                self._find()

            elif command == "6":

                self._update_item()

            elif command == "7":

                self._delete_item()

            elif command == "8":

                self._show_tables()

            elif command == "0":

                print(
                    "Выход"
                )

                break

            else:

                print(
                    "Неизвестная команда"
                )