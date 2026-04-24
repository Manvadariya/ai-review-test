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


if __name__ == "__main__":
    unittest.main()
