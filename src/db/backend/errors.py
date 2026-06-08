class DatabaseError(Exception):
    """Базовое исключение БД."""


class TableAlreadyExistsError(DatabaseError):
    """Таблица уже существует."""


class TableNotFoundError(DatabaseError):
    """Таблица не найдена."""


class DuplicateIdError(DatabaseError):
    """Запись с таким ID уже существует."""


class RecordNotFoundError(DatabaseError):
    """Запись не найдена."""


class InvalidIdError(DatabaseError):
    """Некорректный ID."""


class InvalidFieldError(DatabaseError):
    """Некорректное поле."""


class ValidationError(DatabaseError):
    """Ошибка валидации данных."""