
import json
from pathlib import Path

from .memory import MemoryDB, Table, TYPE_MAP
from .errors import (
    DatabaseError,
    ValidationError,
)


class FileDB(MemoryDB):
    """База данных с хранением таблиц в JSON."""

    def __init__(self, file_path: str = "database.json"):
        super().__init__()
        self.file_path = Path(file_path)
        self._load()

    def _load(self) -> None:
        """Загрузить таблицы из JSON, если файл существует."""
        if not self.file_path.exists():
            return

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

        except (OSError, json.JSONDecodeError) as error:
            raise DatabaseError(
                f"Не удалось прочитать базу данных: {error}"
            ) from error

        if not isinstance(data, dict):
            raise ValidationError(
                "Некорректный формат файла базы данных"
            )

        for table_name, table_data in data.items():
            if not isinstance(table_data, dict):
                raise ValidationError(
                    f"Некорректные данные таблицы '{table_name}'"
                )

            columns = table_data.get("columns")
            rows = table_data.get("rows")

            if not isinstance(columns, dict) or not isinstance(rows, list):
                raise ValidationError(
                    f"Некорректная структура таблицы '{table_name}'"
                )

            schema = {}

            for column_name, type_name in columns.items():
                if type_name not in TYPE_MAP:
                    raise ValidationError(
                        f"Неизвестный тип поля '{column_name}'"
                    )

                schema[column_name] = TYPE_MAP[type_name]

            if "id" not in schema or schema["id"] is not int:
                raise ValidationError(
                    f"В таблице '{table_name}' отсутствует корректный ID"
                )

            table = Table(table_name, schema)

            for row in rows:
                if not isinstance(row, dict):
                    raise ValidationError(
                        f"Некорректная запись в таблице '{table_name}'"
                    )

                table.validate_record(row)

                if any(existing["id"] == row["id"] for existing in table.rows):
                    raise ValidationError(
                        f"Повторяющийся ID в таблице '{table_name}'"
                    )

                table.rows.append(row.copy())

            self.tables[table_name] = table

    def _save(self) -> None:
        """Сохранить таблицы в JSON."""
        data = {}

        for table_name, table in self.tables.items():
            columns = {}

            for column_name, column_type in table.schema.items():
                if column_type is int:
                    columns[column_name] = "int"
                elif column_type is str:
                    columns[column_name] = "str"
                else:
                    raise ValidationError(
                        f"Неподдерживаемый тип поля '{column_name}'"
                    )

            data[table_name] = {
                "columns": columns,
                "rows": table.select(),
            }

        try:
            self.file_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self.file_path.open("w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

        except OSError as error:
            raise DatabaseError(
                f"Не удалось сохранить базу данных: {error}"
            ) from error

    def create_table(self, table_name, columns) -> None:
        super().create_table(table_name, columns)
        self._save()

    def get_table(self, table_name: str) -> Table:
        return super().get_table(table_name)

    def get_tables(self) -> list[str]:
        return super().get_tables()

    def create_item(self, table_name: str, data: dict) -> dict:
        result = self.get_table(table_name).create(data)
        self._save()
        return result

    def select_item(self, table_name: str, filters=None) -> list[dict]:
        return self.get_table(table_name).select(filters)

    def update_item(self, table_name: str, item_id: int, updates: dict) -> dict:
        result = self.get_table(table_name).update(item_id, updates)
        self._save()
        return result

    def delete_item(self, table_name: str, item_id: int) -> None:
        self.get_table(table_name).delete(item_id)
        self._save()
