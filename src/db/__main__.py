from .tui import TUI
from .backend.file import FileDB


def main() -> None:
    db = FileDB("database.json")
    app = TUI(db)
    app.run()


if __name__ == "__main__":
    main()
