from __future__ import annotations
import frappe
from frappe.utils import today
from frappe import _
from foundation.api.payroll import check_payroll_requirements

def compute_payroll_flags(doc, method):
    """
    Hook for Employee.validate (and optionally on_update_after_submit).
    IMPORTANT: Do not .save() here; just mutate fields on 'doc'.
    """
    result = check_payroll_requirements(doc)

    new_enabled = 1 if result["ok"] else 0

    # get previous value once to decide whether to stamp the date
    try:
        prev_enabled = doc.get_db_value("custom_payroll_enabled") or 0
    except Exception:
        # brand new doc (not in DB yet)
        prev_enabled = 0

    doc.custom_payroll_enabled = new_enabled
    doc.custom_payroll_missing_fields = "" if result["ok"] else result["message"]

    # stamp when turning ON for the first time
    if new_enabled and not prev_enabled and not doc.get("custom_payroll_enabled_on"):
        doc.custom_payroll_enabled_on = today()
