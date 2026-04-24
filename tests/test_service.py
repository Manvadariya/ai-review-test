from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from contact_book.repository import ContactRepository
from contact_book.service import ContactBook


class ContactBookTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp_dir = TemporaryDirectory()
        self._contacts_file = Path(self._tmp_dir.name) / "contacts.json"
        self.book = ContactBook(ContactRepository(self._contacts_file))

    def tearDown(self) -> None:
        self._tmp_dir.cleanup()

    def test_add_and_get_contact(self) -> None:
        self.book.add_contact(name="Alice", phone="111", email="alice@mail.com")

        saved = self.book.get_contact("111")
        self.assertIsNotNone(saved)
        self.assertEqual("Alice", saved.name)
        self.assertEqual("alice@mail.com", saved.email)

    def test_add_duplicate_phone_raises_error(self) -> None:
        self.book.add_contact(name="Alice", phone="111")

        with self.assertRaises(ValueError):
            self.book.add_contact(name="Bob", phone="111")

    def test_delete_contact(self) -> None:
        self.book.add_contact(name="Alice", phone="111")

        self.assertTrue(self.book.delete_contact("111"))
        self.assertIsNone(self.book.get_contact("111"))

    def test_update_contact(self) -> None:
        self.book.add_contact(name="Alice", phone="111", email="a@old.com")

        updated = self.book.update_contact(
            "111",
            name="Alice Updated",
            new_phone="222",
            email="a@new.com",
        )

        self.assertEqual("Alice Updated", updated.name)
        self.assertEqual("222", updated.phone)
        self.assertEqual("a@new.com", updated.email)
        self.assertIsNone(self.book.get_contact("111"))
        self.assertIsNotNone(self.book.get_contact("222"))

    def test_search_contacts(self) -> None:
        self.book.add_contact(name="Alice", phone="111", email="alice@mail.com")
        self.book.add_contact(name="Bob", phone="222", address="New York")

        result = self.book.search_contacts("new")
        self.assertEqual(1, len(result))
        self.assertEqual("Bob", result[0].name)

    def test_sort_contacts(self) -> None:
        self.book.add_contact(name="Charlie", phone="333")
        self.book.add_contact(name="Alice", phone="111")
        self.book.add_contact(name="Bob", phone="222")

        sorted_names = [item.name for item in self.book.list_contacts(sort_by="name")]
        self.assertEqual(["Alice", "Bob", "Charlie"], sorted_names)

    def test_persistence_round_trip(self) -> None:
        self.book.add_contact(name="Alice", phone="111")

        reloaded = ContactBook(ContactRepository(self._contacts_file))
        all_contacts = reloaded.list_contacts()
        self.assertEqual(1, len(all_contacts))
        self.assertEqual("Alice", all_contacts[0].name)

    def test_search_contacts_with_field_and_exact_match(self) -> None:
        self.book.add_contact(
            name="Alice Johnson",
            phone="111",
            email="alice@mail.com",
            address="Delhi",
        )
        self.book.add_contact(
            name="Alicia",
            phone="222",
            email="alicia@mail.com",
            address="Mumbai",
        )

        exact_name = self.book.search_contacts("Alice Johnson", field="name", exact=True)
        self.assertEqual(1, len(exact_name))
        self.assertEqual("111", exact_name[0].phone)

        name_partial = self.book.search_contacts("ali", field="name")
        self.assertEqual(2, len(name_partial))

    def test_search_contacts_rejects_invalid_field(self) -> None:
        self.book.add_contact(name="Alice", phone="111")

        with self.assertRaises(ValueError):
            self.book.search_contacts("alice", field="nickname")

    def test_search_contacts_rejects_non_string_query(self) -> None:
        self.book.add_contact(name="Alice", phone="111")

        with self.assertRaises(TypeError):
            self.book.search_contacts(None)  # type: ignore[arg-type]

    def test_search_contacts_rejects_non_string_field(self) -> None:
        self.book.add_contact(name="Alice", phone="111")

        with self.assertRaises(TypeError):
            self.book.search_contacts("alice", field=None)  # type: ignore[arg-type]

    def test_bulk_add_contacts_skip_duplicates(self) -> None:
        summary = self.book.bulk_add_contacts(
            [
                {"name": "Alice", "phone": "111", "email": "alice@old.com"},
                {"name": "Alice Updated", "phone": "111", "email": "alice@new.com"},
                {"name": "Bob", "phone": "222"},
            ],
            on_duplicate="skip",
        )

        self.assertEqual({"added": 2, "updated": 0, "skipped": 1}, summary)
        self.assertEqual("alice@old.com", self.book.get_contact("111").email)

    def test_bulk_add_contacts_update_duplicates(self) -> None:
        self.book.add_contact(name="Alice", phone="111", email="alice@old.com")

        summary = self.book.bulk_add_contacts(
            [{"name": "Alice Updated", "phone": "111", "email": "alice@new.com"}],
            on_duplicate="update",
        )

        self.assertEqual({"added": 0, "updated": 1, "skipped": 0}, summary)
        updated = self.book.get_contact("111")
        self.assertIsNotNone(updated)
        self.assertEqual("Alice Updated", updated.name)
        self.assertEqual("alice@new.com", updated.email)

    def test_bulk_add_contacts_error_on_duplicates(self) -> None:
        self.book.add_contact(name="Alice", phone="111")

        with self.assertRaises(ValueError):
            self.book.bulk_add_contacts(
                [{"name": "Alice Again", "phone": "111"}],
                on_duplicate="error",
            )

    def test_bulk_add_contacts_skips_invalid_entries_in_skip_mode(self) -> None:
        summary = self.book.bulk_add_contacts(
            [
                {"name": "Alice", "phone": "111"},
                {"name": "Missing Phone"},
                {"name": "Bob", "phone": 222},
                {"name": "Charlie", "phone": "333"},
            ],
            on_duplicate="skip",
        )

        self.assertEqual({"added": 2, "updated": 0, "skipped": 2}, summary)
        self.assertIsNotNone(self.book.get_contact("111"))
        self.assertIsNotNone(self.book.get_contact("333"))

    def test_bulk_add_contacts_reports_invalid_index_in_error_mode(self) -> None:
        with self.assertRaises(ValueError) as context:
            self.book.bulk_add_contacts(
                [
                    {"name": "Alice", "phone": "111"},
                    {"name": "Missing Phone"},
                ],
                on_duplicate="error",
            )

        self.assertIn("index 2", str(context.exception))

    def test_bulk_add_contacts_rejects_invalid_contacts_argument(self) -> None:
        with self.assertRaises(TypeError):
            self.book.bulk_add_contacts("not-a-list")  # type: ignore[arg-type]

    def test_bulk_add_contacts_rejects_non_string_on_duplicate(self) -> None:
        with self.assertRaises(TypeError):
            self.book.bulk_add_contacts([], on_duplicate=None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
