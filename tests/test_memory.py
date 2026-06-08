import unittest

from src.db.backend.memory import MemoryDB
from src.db.backend.errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    DuplicateIdError,
    RecordNotFoundError,
    InvalidIdError,
    InvalidFieldError,
    ValidationError,
)


class TestMemory(unittest.TestCase):

    def setUp(self):
        self.db = MemoryDB()
        self.db.create_table(
            "users",
            [("name", "str"), ("age", "int")]
        )
        self.table = self.db.get_table("users")

    # =========================
    # CREATE (success)
    # =========================
    def test_create_success(self):
        record = {"id": 101, "name": "John", "age": 20}
        result = self.table.create(record)
        self.assertEqual(result, record)

    # =========================
    # ID ERRORS
    # =========================
    def test_invalid_id_type(self):
        with self.assertRaises(InvalidIdError):
            self.table.create({"id": "abc", "name": "John", "age": 20})

    def test_invalid_id_length(self):
        with self.assertRaises(InvalidIdError):
            self.table.create({"id": 1, "name": "John", "age": 20})

    # =========================
    # VALIDATION ERRORS
    # =========================
    def test_empty_string_field(self):
        with self.assertRaises(ValidationError):
            self.table.create({"id": 101, "name": "", "age": 20})

    def test_missing_field(self):
        with self.assertRaises(ValidationError):
            self.table.create({"id": 101, "name": "John"})

    def test_wrong_type_field(self):
        with self.assertRaises(ValidationError):
            self.table.create({"id": 101, "name": "John", "age": "20"})

    # =========================
    # DUPLICATE
    # =========================
    def test_duplicate_id(self):
        self.table.create({"id": 101, "name": "John", "age": 20})

        with self.assertRaises(DuplicateIdError):
            self.table.create({"id": 101, "name": "Jane", "age": 22})

    # =========================
    # SELECT
    # =========================
    def test_select_all(self):
        self.table.create({"id": 101, "name": "A", "age": 20})
        self.table.create({"id": 102, "name": "B", "age": 21})

        result = self.table.select()
        self.assertEqual(len(result), 2)

    def test_select_filter(self):
        self.table.create({"id": 101, "name": "A", "age": 20})
        self.table.create({"id": 102, "name": "B", "age": 21})
        self.table.create({"id": 103, "name": "A", "age": 22})

        result = self.table.select({"name": "A"})
        self.assertEqual(len(result), 2)

    def test_select_empty(self):
        result = self.table.select()
        self.assertEqual(result, [])

    # =========================
    # UPDATE
    # =========================
    def test_update_success(self):
        self.table.create({"id": 101, "name": "John", "age": 20})

        updated = self.table.update(101, {"name": "Bob"})
        self.assertEqual(updated["name"], "Bob")

    def test_update_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.update(999, {"name": "X"})

    def test_update_invalid_field(self):
        self.table.create({"id": 101, "name": "John", "age": 20})

        with self.assertRaises(InvalidFieldError):
            self.table.update(101, {"unknown": "X"})

    # =========================
    # DELETE
    # =========================
    def test_delete_success(self):
        self.table.create({"id": 101, "name": "John", "age": 20})

        self.table.delete(101)
        self.assertEqual(self.table.select(), [])

    def test_delete_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.delete(999)

    # =========================
    # SCHEMA / COLUMNS
    # =========================
    def test_schema(self):
        schema = self.table.get_schema()
        self.assertIn("name", schema)
        self.assertIn("age", schema)

    def test_columns(self):
        cols = self.table.get_columns()
        self.assertIn("name", cols)
        self.assertIn("age", cols)

    def test_schema_is_copy(self):
        schema = self.table.get_schema()
        schema["hack"] = int

        self.assertNotIn("hack", self.table.get_schema())

    # =========================
    # DB LEVEL ERRORS
    # =========================
    def test_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.get_table("ghost")

    def test_create_table_duplicate(self):
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table(
                "users",
                [("x", "int")]
            )