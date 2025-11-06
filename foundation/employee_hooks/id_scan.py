from __future__ import annotations
import frappe
from frappe import _
from foundation.api.validate_helpers import (
    ALLOWED_MIME,
    ALLOWED_EXT,
    validate_iran_national_code,
)

def enforce_employee_national_id_attachment_policy(doc, method):
    """
    Employee.before_save:
      - require Employee.national_id_scan
      - require the underlying File row (not just a pasted URL)
      - file must be Private and of allowed type
      - if national_code present, validate it
      - prevent duplicate content_hash across employees
    """
    # --- test-only escape hatch ---
    if getattr(getattr(doc, "flags", object()), "_skip_id_scan", False):
        return
    # --------------------------------

    if not getattr(doc, "national_id_scan", None):
        frappe.throw(_("National ID Scan is required."))

    files = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Employee",
            "attached_to_name": doc.name,
            "attached_to_field": "national_id_scan",
        },
        fields=["name", "is_private", "mime_type", "file_name", "content_hash"],
        limit=1,
    )
    if not files:
        frappe.throw(_("Upload the National ID to the field (don’t paste a URL)."))

    f = files[0]
    if not f.get("is_private"):
        frappe.throw(_("National ID files must be Private."))

    fn = (f.get("file_name") or "").lower()
    mime_ok = f.get("mime_type") in ALLOWED_MIME if f.get("mime_type") else False
    ext_ok  = fn.endswith(ALLOWED_EXT)
    if not (mime_ok or ext_ok):
        frappe.throw(_("Only PDF, JPG, JPEG, or PNG is allowed for National ID Scan."))

    if hasattr(doc, "national_code") and getattr(doc, "national_code", None):
        if not validate_iran_national_code(doc.national_code or ""):
            frappe.throw(_("National Code is invalid. Please check the 10-digit number."))

    ch = f.get("content_hash")
    if ch:
        dup = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Employee",
                "attached_to_field": "national_id_scan",
                "content_hash": ch,
                "attached_to_name": ["!=", doc.name],
            },
            pluck="attached_to_name",
            limit=1,
        )
        if dup:
            frappe.throw(_("This exact file is already attached to another Employee."))

