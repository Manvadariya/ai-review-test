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

    def search_contacts(self, query: str) -> list[Contact]:
        needle = query.strip().lower()
        if not needle:
            return self.list_contacts()

        matches = [
            contact
            for contact in self._contacts.values()
            if needle in contact.name.lower()
            or needle in contact.phone.lower()
            or needle in contact.email.lower()
            or needle in contact.address.lower()
        ]
        return sorted(matches, key=lambda item: (item.name.lower(), item.phone.lower()))

    def list_contacts(self, sort_by: str = "name") -> list[Contact]:
        key = sort_by.strip().lower()
        if key not in {"name", "phone", "email"}:
            raise ValueError("sort_by must be one of: name, phone, email")

        return sorted(
            self._contacts.values(),
            key=lambda item: (getattr(item, key).lower(), item.phone.lower()),
        )
