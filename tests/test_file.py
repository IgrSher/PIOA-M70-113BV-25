
import pytest

from src.db.backend.file import FileDB
from src.db.backend.errors import DatabaseError, ValidationError


def test_data_is_saved_and_loaded(tmp_path):
    file_path = tmp_path / "database.json"

    db = FileDB(str(file_path))
    db.create_table("users", [("name", "str"), ("age", "int")])

    db.create_item("users", {
        "id": 101,
        "name": "Alex",
        "age": 20
    })

    loaded_db = FileDB(str(file_path))

    result = loaded_db.select_item("users")

    assert result == [{
        "id": 101,
        "name": "Alex",
        "age": 20
    }]


def test_update_is_saved(tmp_path):
    file_path = tmp_path / "database.json"

    db = FileDB(str(file_path))
    db.create_table("users", [("name", "str"), ("age", "int")])

    db.create_item("users", {
        "id": 101,
        "name": "Alex",
        "age": 20
    })

    db.update_item("users", 101, {"age": 25})

    loaded_db = FileDB(str(file_path))

    result = loaded_db.select_item("users")

    assert result[0]["age"] == 25


def test_delete_is_saved(tmp_path):
    file_path = tmp_path / "database.json"

    db = FileDB(str(file_path))
    db.create_table("users", [("name", "str"), ("age", "int")])

    db.create_item("users", {
        "id": 101,
        "name": "Alex",
        "age": 20
    })

    db.delete_item("users", 101)

    loaded_db = FileDB(str(file_path))

    assert loaded_db.select_item("users") == []
def test_missing_file_starts_empty(tmp_path):
    file_path = tmp_path / "database.json"

    db = FileDB(str(file_path))

    assert db.get_tables() == []


def test_invalid_json_raises_database_error(tmp_path):
    file_path = tmp_path / "database.json"
    file_path.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(DatabaseError):
        FileDB(str(file_path))


def test_invalid_database_structure_raises_validation_error(tmp_path):
    file_path = tmp_path / "database.json"
    file_path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValidationError):
        FileDB(str(file_path))