import re
from pydantic import BaseModel, field_validator, Field


# Allowed characters: digits, spaces, dashes, plus sign (leading only)
# Accepted formats: +380XXXXXXXXX or 0XXXXXXXXX (9 digits after prefix)
PHONE_RE = re.compile(r"^(\+380|0)[\d \-]{9,13}$")


class LeadRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        stripped = v.strip()
        if not PHONE_RE.match(stripped):
            raise ValueError("Введіть номер у форматі +380XXXXXXXXX або 0XXXXXXXXX")
        digit_count = sum(c.isdigit() for c in stripped)
        # +380 prefix = 3 digits, operator+number = 9 digits → total 12
        # 0 prefix = 1 digit, operator+number = 9 digits → total 10
        expected = 12 if stripped.startswith("+") else 10
        if digit_count != expected:
            raise ValueError("Введіть номер у форматі +380XXXXXXXXX або 0XXXXXXXXX")
        return stripped

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


class LeadResponse(BaseModel):
    ok: bool
    message: str
