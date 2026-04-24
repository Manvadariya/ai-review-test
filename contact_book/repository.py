from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from .models import Contact


class ContactRepository:
    """Persists contacts to a JSON file."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def load(self) -> dict[str, Contact]:
        if not self.file_path.exists():
            return {}

        content = self.file_path.read_text(encoding="utf-8").strip()
        if not content:
            return {}

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {self.file_path}") from exc

        if not isinstance(payload, list):
            raise ValueError("Contact file must contain a list of contacts.")

        contacts: dict[str, Contact] = {}
        for item in payload:
            if not isinstance(item, dict):
                continue
            contact = Contact.from_dict(item)
            contacts[contact.phone] = contact

        return contacts

    def save(self, contacts: Mapping[str, Contact]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [contact.to_dict() for contact in contacts.values()]
        self.file_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
