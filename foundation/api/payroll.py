from __future__ import annotations
import re
import frappe
from frappe import _
from frappe.utils import today
from .validate_helpers import label, is_valid_sheba, is_phone

ALLOWED_CONTRACT_TYPES = {"Experimental", "Permanent"}

# ---------- pure checker (no DB writes) ----------
def check_payroll_requirements(emp_doc) -> dict:
    """
    Given an Employee *doc* (not name), return {ok, missing, invalid, message}.
    No save/commit here — safe for hooks.
    """
    required = [
        "passport_number",
        "bank_name",
        "bank_ac_no",
        "custom_shaba_no",
        "marital_status",
        "person_to_be_contacted",
        "emergency_phone_number",
        "relation",
        "custom_contract_type",
    ]

    missing, invalid = [], []

    # presence
    for fn in required:
        if not emp_doc.get(fn):
            missing.append(label(fn))

    # need at least one education row (child table)
    if not (emp_doc.get("education") or []):
        missing.append(_("Education (at least one record)"))

    # value/format checks
    ct = (emp_doc.get("custom_contract_type") or "").strip()
    if ct and ct not in ALLOWED_CONTRACT_TYPES:
        invalid.append(label("custom_contract_type"))

    if emp_doc.get("custom_shaba_no") and not is_valid_sheba(emp_doc.custom_shaba_no):
        invalid.append(label("custom_shaba_no"))

    if emp_doc.get("bank_ac_no") and not re.fullmatch(r"\d{6,24}", str(emp_doc.bank_ac_no or "")):
        invalid.append(label("bank_ac_no"))

    if emp_doc.get("emergency_phone_number") and not is_phone(emp_doc.emergency_phone_number):
        invalid.append(label("emergency_phone_number"))

    parts = []
    if missing:
        parts.append(_("Missing:"))
        parts += [f"• {m}" for m in missing]
    if invalid:
        parts.append(_("Invalid format:"))
        parts += [f"• {v}" for v in invalid]
    msg_text = "\n".join(parts)

    return {
        "ok": not missing and not invalid,
        "missing": missing,
        "invalid": invalid,
        "message": msg_text,
    }

# ---------- API endpoint (manual call / button) ----------
@frappe.whitelist()
def validate_employee_payroll(employee: str) -> dict:
    """
    Manual validator (e.g., from a button). Loads doc, runs checks, writes flags,
    and saves once. Safe to call from UI or scripts.
    """
    emp = frappe.get_doc("Employee", employee)
    result = check_payroll_requirements(emp)

    # derive new flags
    enable_now = 1 if result["ok"] else 0
    prev_enabled = frappe.db.get_value("Employee", emp.name, "custom_payroll_enabled") or 0

    emp.custom_payroll_enabled = enable_now
    emp.custom_payroll_missing_fields = "" if result["ok"] else result["message"]
    # stamp the date only when transitioning 0 -> 1
    if enable_now and not prev_enabled:
        emp.custom_payroll_enabled_on = today()

    emp.save(ignore_permissions=True)
    frappe.db.commit()
    return {
        **result,
        "enabled": emp.custom_payroll_enabled,
        "enabled_on": emp.custom_payroll_enabled_on,
    }
