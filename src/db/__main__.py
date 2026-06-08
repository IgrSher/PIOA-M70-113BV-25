from .tui import TUI


def main() -> None:
    app = TUI()
    app.run()


if __name__ == "__main__":
    main()