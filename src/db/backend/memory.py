from .errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    DuplicateIdError,
    RecordNotFoundError,
    InvalidIdError,
    InvalidFieldError,
    ValidationError,
)

TYPE_MAP = {
    "int": int,
    "str": str,
}

ID_LENGTH = 3


class Table:
    def __init__(self, name: str, schema: dict[str, type]):
        self.name = name
        self.schema = schema
        self.rows: list[dict] = []

    def validate_record(self, record: dict) -> None:
        if "id" not in record:
            raise InvalidIdError("Отсутствует ID")

        item_id = record["id"]

        if not isinstance(item_id, int):
            raise InvalidIdError(
                "ID должен быть целым числом"
            )

        if len(str(abs(item_id))) != ID_LENGTH:
            raise InvalidIdError(
                "ID должен содержать 3 цифры"
            )

        for field_name, field_type in self.schema.items():

            if field_name not in record:
                raise ValidationError(
                    f"Поле '{field_name}' отсутствует"
                )

            value = record[field_name]

            if field_type is int:

                if not isinstance(value, int):
                    raise ValidationError(
                        f"Поле '{field_name}' "
                        f"должно быть int"
                    )

            elif field_type is str:

                if (
                    not isinstance(value, str)
                    or not value.strip()
                ):
                    raise ValidationError(
                        f"Поле '{field_name}' "
                        f"должно быть непустой строкой"
                    )

    def create(self, data: dict) -> dict:
        self.validate_record(data)

        for row in self.rows:

            if row["id"] == data["id"]:
                raise DuplicateIdError(
                    f"Запись с ID "
                    f"{data['id']} уже существует"
                )

        self.rows.append(data.copy())

        return data.copy()

    def select(
        self,
        filters: dict | None = None
    ) -> list[dict]:

        if not filters:
            return [
                row.copy()
                for row in self.rows
            ]

        result = []

        for row in self.rows:

            matched = True

            for field, value in filters.items():

                if row.get(field) != value:
                    matched = False
                    break

            if matched:
                result.append(row.copy())

        return result

    def update(
        self,
        item_id: int,
        updates: dict
    ) -> dict:

        for row in self.rows:

            if row["id"] == item_id:

                updated = row.copy()

                for key, value in updates.items():

                    if key == "id":
                        continue

                    if key not in self.schema:
                        raise InvalidFieldError(
                            f"Поле '{key}' "
                            f"не существует"
                        )

                    updated[key] = value

                self.validate_record(updated)

                row.clear()
                row.update(updated)

                return updated.copy()

        raise RecordNotFoundError(
            f"Запись с ID "
            f"{item_id} не найдена"
        )

    def delete(
        self,
        item_id: int
    ) -> None:

        for index, row in enumerate(self.rows):

            if row["id"] == item_id:

                del self.rows[index]
                return

        raise RecordNotFoundError(
            f"Запись с ID "
            f"{item_id} не найдена"
        )

    def get_schema(self) -> dict[str, type]:
        return self.schema.copy()

    def get_columns(self) -> list[str]:
        return list(self.schema.keys())


class MemoryDB:
    def __init__(self):
        self.tables: dict[str, Table] = {}

    def create_table(
        self,
        table_name: str,
        columns: list[tuple[str, str]]
    ) -> None:

        table_name = table_name.strip()

        if not table_name:
            raise ValidationError(
                "Имя таблицы не может быть пустым"
            )

        if table_name in self.tables:
            raise TableAlreadyExistsError(
                f"Таблица '{table_name}' "
                f"уже существует"
            )

        schema = {
            "id": int
        }

        for column_name, column_type in columns:

            column_name = column_name.strip()
            column_type = (
                column_type
                .strip()
                .lower()
            )

            if not column_name:
                raise ValidationError(
                    "Имя столбца "
                    "не может быть пустым"
                )

            if column_name == "id":
                raise ValidationError(
                    "Столбец 'id' "
                    "создаётся автоматически"
                )

            if column_name in schema:
                raise ValidationError(
                    f"Столбец '{column_name}' "
                    f"уже существует"
                )

            if column_type not in TYPE_MAP:
                raise ValidationError(
                    "Допустимые типы: int, str"
                )

            schema[column_name] = (
                TYPE_MAP[column_type]
            )

        self.tables[table_name] = Table(
            table_name,
            schema
        )

    def get_table(
        self,
        table_name: str
    ) -> Table:

        if table_name not in self.tables:
            raise TableNotFoundError(
                f"Таблица '{table_name}' "
                f"не существует"
            )

        return self.tables[table_name]


_db = MemoryDB()


def create_table(
    table_name: str,
    columns: list[tuple[str, str]]
) -> None:
    _db.create_table(
        table_name,
        columns
    )


def create_item(
    table_name: str,
    data: dict
) -> dict:
    return (
        _db
        .get_table(table_name)
        .create(data)
    )


def select_item(
    table_name: str,
    filters: dict | None = None
) -> list[dict]:
    return (
        _db
        .get_table(table_name)
        .select(filters)
    )


def update_item(
    table_name: str,
    item_id: int,
    updates: dict
) -> dict:
    return (
        _db
        .get_table(table_name)
        .update(item_id, updates)
    )


def delete_item(
    table_name: str,
    item_id: int
) -> None:
    _db.get_table(
        table_name
    ).delete(item_id)


def get_schema(
    table_name: str
) -> dict[str, type]:
    return (
        _db
        .get_table(table_name)
        .get_schema()
    )


def get_columns(
    table_name: str
) -> list[str]:
    return (
        _db
        .get_table(table_name)
        .get_columns()
    )


def get_tables() -> list[str]:
    return list(_db.tables.keys())