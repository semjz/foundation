# -*- coding: utf-8 -*-
# transport/employee_hooks/checklist.py

import re
import frappe

# ----- regex patterns for file-name/url detection (adjust if needed)
P_ID   = [r"کارت\s*ملی", r"\bnational\b", r"\bmeli\b", r"\bid\s*card\b"]
P_FRT  = [r"\bfront\b", r"جلو", r"رو"]
P_BCK  = [r"\bback\b",  r"پشت"]
# ⬇️ Only change made here: added tokens to catch shen-full.* style names
P_SHEN = [r"شناسنامه", r"birth\s*certificate", r"\bshenas", r"\bshen\b", r"shen"]
P_EDU  = [r"مدرک", r"تحصیلی", r"\bdegree\b", r"\bdiploma\b", r"\bcertificate\b"]
P_CON  = [r"قرارداد", r"\bcontract\b", r"\bsigned\b"]

CHECKLIST_DT = "Employee Checklist"          # your checklist doctype name
CHECKLIST_EMP_LINK_FLD = "employee"   # your actual link field to Employee

# Map logical flags -> your actual custom_* fields on Employee Checklist
FLAG_FIELD_MAP = {
    "id_card_both_sides":    "custom_id_card_both_sides",
    "shenasnameh_full":      "custom_shenasnameh_full",
    "education_last_degree": "custom_education_last_degree",
    "signed_contract":       "custom_signed_contract",
}

# ================= core helpers =================

def _m(text, patterns):
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)

def _attached_file_blobs(employee_name: str):
    rows = frappe.get_all(
        "File",
        filters={"attached_to_doctype": "Employee", "attached_to_name": employee_name},
        fields=["file_name", "file_url"],
    )
    return [(r.get("file_name") or "") + " " + (r.get("file_url") or "") for r in rows]

def _compute_flags(employee_name: str) -> dict:
    """Derive 4 booleans from attached files (by filename/url keywords)."""
    blobs = _attached_file_blobs(employee_name)
    if not blobs:
        return dict(
            id_card_both_sides=0,
            shenasnameh_full=0,
            education_last_degree=0,
            signed_contract=0,
        )

    has_front = any(_m(b, P_FRT) for b in blobs)
    has_back  = any(_m(b, P_BCK) for b in blobs)
    is_id_any = any(_m(b, P_ID)  for b in blobs)
    id_ok = (has_front and has_back) or is_id_any

    sh_ok  = any(_m(b, P_SHEN) for b in blobs)
    edu_ok = any(_m(b, P_EDU)  for b in blobs)
    co_ok  = any(_m(b, P_CON)  for b in blobs)

    return dict(
        id_card_both_sides=1 if id_ok else 0,
        shenasnameh_full=1 if sh_ok else 0,
        education_last_degree=1 if edu_ok else 0,
        signed_contract=1 if co_ok else 0,
    )

def _ensure_checklist(employee_name: str):
    """Create checklist row if it doesn't exist; return its name (or None if DT missing)."""
    if not frappe.db.exists("DocType", CHECKLIST_DT):
        return None

    name = frappe.db.get_value(CHECKLIST_DT, {CHECKLIST_EMP_LINK_FLD: employee_name}, "name")
    if name:
        return name

    doc = frappe.get_doc({"doctype": CHECKLIST_DT, CHECKLIST_EMP_LINK_FLD: employee_name})
    doc.insert(ignore_permissions=True)
    return doc.name

def _apply_flags(employee_name: str, logical_flags: dict):
    """
    Translate logical flags to custom_* fields and update only existing ones.
    Avoids selecting missing columns; does not bump modified.
    """
    if not frappe.db.exists("DocType", CHECKLIST_DT):
        return

    name = _ensure_checklist(employee_name)
    if not name:
        return

    meta = frappe.get_meta(CHECKLIST_DT)
    existing = {df.fieldname for df in meta.fields}

    chk = frappe.get_doc(CHECKLIST_DT, name)

    updates = {}
    for logical_key, value in logical_flags.items():
        target_field = FLAG_FIELD_MAP.get(logical_key)
        if not target_field or target_field not in existing:
            continue  # skip if the custom_* field doesn't exist on this site
        cur_val = int(getattr(chk, target_field, 0) or 0)
        new_val = int(value or 0)
        if cur_val != new_val:
            updates[target_field] = new_val

    if updates:
        frappe.db.set_value(CHECKLIST_DT, name, updates, update_modified=False)

# ================= hooks =================

def employee_after_insert(doc, method=None):
    """Prepare checklist row once an Employee is created (no tick computation here)."""
    _ensure_checklist(doc.name)

def file_after_insert(doc, method=None):
    """On any file attached to an Employee, recompute ticks."""
    if doc.attached_to_doctype == "Employee" and doc.attached_to_name:
        flags = _compute_flags(doc.attached_to_name)
        _apply_flags(doc.attached_to_name, flags)

def file_after_delete(doc, method=None):
    """On file removal from an Employee, recompute ticks."""
    if doc.attached_to_doctype == "Employee" and doc.attached_to_name:
        flags = _compute_flags(doc.attached_to_name)
        _apply_flags(doc.attached_to_name, flags)

# ============== optional: manual refresh API ==============

@frappe.whitelist()
def refresh_employee_checklist(employee: str):
    flags = _compute_flags(employee)
    _apply_flags(employee, flags)
    return flags
