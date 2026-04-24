from __future__ import annotations

from dataclasses import dataclass


def _clean(value: str) -> str:
    return value.strip()


@dataclass(slots=True)
class Contact:
    name: str
    phone: str
    email: str = ""
    address: str = ""

    def __post_init__(self) -> None:
        self.name = _clean(self.name)
        self.phone = _clean(self.phone)
        self.email = _clean(self.email)
        self.address = _clean(self.address)

        if not self.name:
            raise ValueError("Name is required.")
        if not self.phone:
            raise ValueError("Phone is required.")

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Contact":
        return cls(
            name=str(data.get("name", "")),
            phone=str(data.get("phone", "")),
            email=str(data.get("email", "")),
            address=str(data.get("address", "")),
        )
