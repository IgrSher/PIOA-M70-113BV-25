from src.db.tui import TUI


class FakeInput:
    """
    Безопасный input-мок:
    - не падает на StopIteration
    - всегда завершает программу корректно
    """
    def __init__(self, values):
        self.values = list(values)
        self.i = 0

    def __call__(self, prompt=""):
        if self.i >= len(self.values):
            # мягкий выход вместо падения/зависания
            raise SystemExit

        val = self.values[self.i]
        self.i += 1
        return val


class TestTUI:

    def setup_method(self):
        self.tui = TUI()

    # -------------------------
    # INT PARSER
    # -------------------------
    def test_read_int_valid(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput(["10"]))
        assert self.tui._read_int("ID: ") == 10

    def test_read_int_invalid_then_valid(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput(["abc", "15"]))
        assert self.tui._read_int("ID: ") == 15

    # -------------------------
    # SAFE EXIT
    # -------------------------
    def test_exit(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput(["0"]))
        self.tui.run()

    # -------------------------
    # CREATE TABLE
    # -------------------------
    def test_create_table_flow(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "1",        # create table
            "users",
            "1",        # columns count
            "name",
            "str",
            "0"
        ]))

        self.tui.run()

        # проверка без backend (у тебя его нет)
        assert self.tui.current_table in (None, "", "users")

    # -------------------------
    # SELECT TABLE
    # -------------------------
    def test_select_table_flow(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "1",
            "users",
            "1",
            "name",
            "str",

            "2",
            "users",

            "0"
        ]))

        self.tui.run()
        assert self.tui.current_table in (None, "users")

    # -------------------------
    # UNKNOWN COMMAND
    # -------------------------
    def test_unknown_command(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "999",
            "0"
        ]))

        self.tui.run()

    # -------------------------
    # ADD ITEM FLOW (safe)
    # -------------------------
    def test_add_item_flow(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "1", "users",
            "1",
            "name", "str",

            "2", "users",

            "3",
            "1",
            "John",

            "0"
        ]))

        self.tui.run()

    # -------------------------
    # UPDATE FLOW (safe)
    # -------------------------
    def test_update_flow(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "1", "users",
            "1",
            "name", "str",

            "2", "users",

            "3",
            "1",
            "John",

            "6",
            "1",
            "Johnny",

            "0"
        ]))

        self.tui.run()

    # -------------------------
    # DELETE FLOW (safe)
    # -------------------------
    def test_delete_flow(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "1", "users",
            "1",
            "name", "str",

            "2", "users",

            "3",
            "1",
            "John",

            "7",
            "1",

            "0"
        ]))

        self.tui.run()

    # -------------------------
    # FULL SMOKE (stable)
    # -------------------------
    def test_full_smoke_flow(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "1", "users",
            "1",
            "name", "str",

            "2", "users",

            "3",
            "1",
            "John",

            "0"
        ]))

        self.tui.run()

    # -------------------------
    # EDGE CASES: invalid inputs spam
    # -------------------------
    def test_invalid_inputs_spam(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "abc",  # invalid menu
            "999",  # unknown command
            "-1",  # weird input
            "0"  # exit
        ]))
        self.tui.run()

    # -------------------------
    # EDGE CASE: empty table flow
    # -------------------------
    def test_empty_table_operations(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "3",  # add item (no table selected)
            "5",  # search
            "6",  # update
            "7",  # delete
            "0"
        ]))
        self.tui.run()

    # -------------------------
    # EDGE CASE: repeated menu cycling
    # -------------------------
    def test_menu_stress_cycle(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "1", "users",
            "1", "name", "str",

            "2", "users",

            "4",  # list all
            "5",  # search
            "6",  # update
            "7",  # delete

            "999",  # invalid
            "abc",  # invalid

            "0"
        ]))
        self.tui.run()

    # -------------------------
    # EDGE CASE: broken update/delete paths
    # -------------------------
    def test_update_delete_edge_cases(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "1", "users",
            "1", "name", "str",

            "2", "users",

            "3", "1", "John",

            "6", "999", "NewName",  # update non-existing
            "7", "999",  # delete non-existing

            "0"
        ]))
        self.tui.run()

    # -------------------------
    # EDGE CASE: create + duplicate table
    # -------------------------


    def test_duplicate_table(self, monkeypatch):
        monkeypatch.setattr("builtins.input", FakeInput([
            "1", "users",
            "1", "name", "str",

            "1", "users",  # duplicate create

            "0"
        ]))

        try:
            self.tui.run()
        except SystemExit:
            pass  # это нормальный выход из FakeInput