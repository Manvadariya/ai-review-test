from __future__ import annotations

from .models import Contact
from .repository import ContactRepository


class ContactBook:
    """Business logic layer for CRUD operations."""

    def __init__(self, repository: ContactRepository) -> None:
        self._repository = repository
        self._contacts: dict[str, Contact] = self._repository.load()

    def add_contact(
        self,
        *,
        name: str,
        phone: str,
        email: str = "",
        address: str = "",
    ) -> Contact:
        contact = Contact(name=name, phone=phone, email=email, address=address)

        if contact.phone in self._contacts:
            raise ValueError("A contact with this phone already exists.")

        self._contacts[contact.phone] = contact
        self._repository.save(self._contacts)
        return contact

    def get_contact(self, phone: str) -> Contact | None:
        return self._contacts.get(phone.strip())

    def delete_contact(self, phone: str) -> bool:
        key = phone.strip()
        if key not in self._contacts:
            return False

        del self._contacts[key]
        self._repository.save(self._contacts)
        return True

    def update_contact(
        self,
        phone: str,
        *,
        name: str | None = None,
        new_phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
    ) -> Contact:
        existing = self.get_contact(phone)
        if existing is None:
            raise KeyError("Contact not found.")

        updated = Contact(
            name=name if name is not None else existing.name,
            phone=new_phone if new_phone is not None else existing.phone,
            email=email if email is not None else existing.email,
            address=address if address is not None else existing.address,
        )

        old_key = existing.phone
        if updated.phone != old_key and updated.phone in self._contacts:
            raise ValueError("Another contact already uses this phone.")

        del self._contacts[old_key]
        self._contacts[updated.phone] = updated
        self._repository.save(self._contacts)
        return updated

    def search_contacts(
        self,
        query: str,
        *,
        field: str = "all",
        exact: bool = False,
    ) -> list[Contact]:
        if not isinstance(query, str):
            raise TypeError("query must be a string")
        if not isinstance(field, str):
            raise TypeError("field must be a string")
        if not isinstance(exact, bool):
            raise TypeError("exact must be a boolean")

        needle = query.strip().lower()
        selected_field = field.strip().lower()
        allowed_fields = {"all", "name", "phone", "email", "address"}

        if selected_field not in allowed_fields:
            raise ValueError("field must be one of: all, name, phone, email, address")

        if not needle:
            return self.list_contacts()

        def _matches(value: str) -> bool:
            lowered_value = value.lower()
            return lowered_value == needle if exact else needle in lowered_value

        matches: list[Contact] = []
        for contact in self._contacts.values():
            if selected_field == "all":
                if (
                    _matches(contact.name)
                    or _matches(contact.phone)
                    or _matches(contact.email)
                    or _matches(contact.address)
                ):
                    matches.append(contact)
                continue

            if _matches(getattr(contact, selected_field)):
                matches.append(contact)

        return sorted(matches, key=lambda item: (item.name.lower(), item.phone.lower()))

    def bulk_add_contacts(
        self,
        contacts: list[dict[str, str]],
        *,
        on_duplicate: str = "skip",
    ) -> dict[str, int]:
        if not isinstance(contacts, list):
            raise TypeError("contacts must be a list of dictionaries")
        if not isinstance(on_duplicate, str):
            raise TypeError("on_duplicate must be a string")

        mode = on_duplicate.strip().lower()
        if mode not in {"skip", "update", "error"}:
            raise ValueError("on_duplicate must be one of: skip, update, error")

        summary = {"added": 0, "updated": 0, "skipped": 0}
        changed = False

        for index, raw_contact in enumerate(contacts, start=1):
            if not isinstance(raw_contact, dict):
                message = f"Invalid contact entry at index {index}: entry must be a dictionary."
                if mode == "error":
                    raise ValueError(message)
                summary["skipped"] += 1
                continue

            try:
                for required_field in ("name", "phone"):
                    if required_field not in raw_contact:
                        raise ValueError(f"missing required field '{required_field}'")
                    if not isinstance(raw_contact[required_field], str):
                        raise ValueError(f"field '{required_field}' must be a string")

                for optional_field in ("email", "address"):
                    if optional_field in raw_contact and not isinstance(raw_contact[optional_field], str):
                        raise ValueError(f"field '{optional_field}' must be a string")

                candidate = Contact.from_dict(raw_contact)
            except (TypeError, ValueError) as exc:
                message = f"Invalid contact entry at index {index}: {exc}"
                if mode == "error":
                    raise ValueError(message) from exc
                summary["skipped"] += 1
                continue

            existing = self._contacts.get(candidate.phone)

            if existing is None:
                self._contacts[candidate.phone] = candidate
                summary["added"] += 1
                changed = True
                continue

            if mode == "skip":
                summary["skipped"] += 1
                continue

            if mode == "error":
                raise ValueError(f"Duplicate phone '{candidate.phone}' at index {index}.")

            self._contacts[candidate.phone] = candidate
            summary["updated"] += 1
            changed = True

        if changed:
            self._repository.save(self._contacts)

        return summary

    def list_contacts(self, sort_by: str = "name") -> list[Contact]:
        key = sort_by.strip().lower()
        if key not in {"name", "phone", "email"}:
            raise ValueError("sort_by must be one of: name, phone, email")

        return sorted(
            self._contacts.values(),
            key=lambda item: (getattr(item, key).lower(), item.phone.lower()),
        )