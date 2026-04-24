from __future__ import annotations

from .models import Contact
from .service import ContactBook


def _print_contact(contact: Contact) -> None:
    print(f"Name   : {contact.name}")
    print(f"Phone  : {contact.phone}")
    print(f"Email  : {contact.email or '-'}")
    print(f"Address: {contact.address or '-'}")
    print("-" * 30)


def _print_contacts(contacts: list[Contact]) -> None:
    if not contacts:
        print("No contacts found.")
        return

    for contact in contacts:
        _print_contact(contact)


def run_cli(book: ContactBook) -> None:
    menu = """
Contact Book
1. Add contact
2. Search contacts
3. Update contact
4. Delete contact
5. View sorted contacts
6. Exit
"""

    while True:
        print(menu)
        choice = input("Choose an option (1-6): ").strip()

        try:
            if choice == "1":
                name = input("Name: ")
                phone = input("Phone: ")
                email = input("Email (optional): ")
                address = input("Address (optional): ")
                created = book.add_contact(
                    name=name,
                    phone=phone,
                    email=email,
                    address=address,
                )
                print(f"Saved: {created.name} ({created.phone})")

            elif choice == "2":
                query = input("Search text (name/phone/email/address): ")
                _print_contacts(book.search_contacts(query))

            elif choice == "3":
                phone = input("Current phone of contact to update: ").strip()
                existing = book.get_contact(phone)
                if existing is None:
                    print("Contact not found.")
                    continue

                print("Leave field empty to keep current value.")
                name = input(f"Name [{existing.name}]: ").strip()
                new_phone = input(f"Phone [{existing.phone}]: ").strip()
                email = input(f"Email [{existing.email}]: ").strip()
                address = input(f"Address [{existing.address}]: ").strip()

                updated = book.update_contact(
                    phone,
                    name=name or None,
                    new_phone=new_phone or None,
                    email=email or None,
                    address=address or None,
                )
                print(f"Updated: {updated.name} ({updated.phone})")

            elif choice == "4":
                phone = input("Phone to delete: ").strip()
                if book.delete_contact(phone):
                    print("Contact deleted.")
                else:
                    print("Contact not found.")

            elif choice == "5":
                sort_by = input("Sort by (name/phone/email): ").strip().lower() or "name"
                _print_contacts(book.list_contacts(sort_by=sort_by))

            elif choice == "6":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Try 1-6.")

        except (ValueError, KeyError) as exc:
            print(f"Error: {exc}")
