from __future__ import annotations

from pathlib import Path

from contact_book.cli import run_cli
from contact_book.repository import ContactRepository
from contact_book.service import ContactBook


def main() -> None:
    repository = ContactRepository(Path("contacts.json"))
    book = ContactBook(repository)
    run_cli(book)


if __name__ == "__main__":
    main()
