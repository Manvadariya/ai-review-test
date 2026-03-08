import tempfile
import unittest
from pathlib import Path

from todo_app import TodoListModel


class TestTodoListModel(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_path = Path(self.temp_dir.name) / "todos.json"
        self.model = TodoListModel(self.storage_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_item_ignores_blank_input(self) -> None:
        self.assertFalse(self.model.add_item("   "))
        self.assertEqual(self.model.items, [])

    def test_add_item_persists_text(self) -> None:
        self.assertTrue(self.model.add_item("Buy groceries"))

        reloaded = TodoListModel(self.storage_path)
        reloaded.load()

        self.assertEqual(len(reloaded.items), 1)
        self.assertEqual(reloaded.items[0].text, "Buy groceries")
        self.assertFalse(reloaded.items[0].completed)

    def test_toggle_selected_flips_status(self) -> None:
        self.model.add_item("Write tests")

        self.assertTrue(self.model.toggle_selected())
        self.assertTrue(self.model.items[0].completed)

    def test_delete_selected_updates_selection(self) -> None:
        self.model.add_item("First")
        self.model.add_item("Second")

        self.assertTrue(self.model.delete_selected())

        self.assertEqual([item.text for item in self.model.items], ["First"])
        self.assertEqual(self.model.selected_index, 0)

    def test_move_selection_wraps(self) -> None:
        self.model.add_item("One")
        self.model.add_item("Two")
        self.model.selected_index = 0

        self.model.move_selection(-1)

        self.assertEqual(self.model.selected_index, 1)


if __name__ == "__main__":
    unittest.main()