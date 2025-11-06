# foundation/api/validate_helpers.py
# keep helpers small & generic
from __future__ import annotations
import re
import frappe

# -------- File / attachment helpers (for ID scans etc.) --------
ALLOWED_MIME = {"application/pdf", "image/jpeg", "image/png"}
ALLOWED_EXT  = (".pdf", ".jpg", ".jpeg", ".png")

# -------- Iran national code (کد ملی) validator --------
def validate_iran_national_code(code: str | None) -> bool:
    """
    Returns True iff `code` is a valid 10-digit Iranian national code.
    Rules:
      - Must be exactly 10 digits
      - Not all digits identical
      - Mod 11 checksum
    """
    if not code:
        return False
    s = re.sub(r"\D+", "", str(code))
    if len(s) != 10:
        return False
    # reject all identical digits (e.g., 0000000000, 1111111111, …)
    if len(set(s)) == 1:
        return False

    digits = list(map(int, s))
    check = digits[9]
    # weighted sum of first 9 digits with weights 10..2
    total = sum(d * w for d, w in zip(digits[:9], range(10, 1, -1)))
    r = total % 11
    calc = r if r < 2 else (11 - r)
    return check == calc

# -------- UI label fetcher (for messaging) --------
def label(fieldname: str) -> str:
    meta = frappe.get_meta("Employee")
    for df in meta.fields:
        if df.fieldname == fieldname:
            return df.label or fieldname
    return fieldname

# -------- Banking / contact validators --------
def is_valid_sheba(v: str | None) -> bool:
    if not v:
        return False
    s = (v or "").replace(" ", "").upper()
    if not (s.startswith("IR") and len(s) == 26):
        return False
    t = s[4:] + s[:4]
    n = "".join(str(ord(c) - 55) if c.isalpha() else c for c in t)
    r = 0
    for ch in n:
        r = (r * 10 + int(ch)) % 97
    return r == 1

def is_phone(v: str | None) -> bool:
    return bool(v) and re.fullmatch(r"\+?\d{8,15}", (v or "").replace(" ", "")) is not None

__all__ = [
    "ALLOWED_MIME",
    "ALLOWED_EXT",
    "validate_iran_national_code",
    "label",
    "is_valid_sheba",
    "is_phone",
]
