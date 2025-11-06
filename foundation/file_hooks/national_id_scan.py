from __future__ import annotations
import frappe
from frappe import _
from foundation.api.validate_helpers import ALLOWED_MIME, ALLOWED_EXT

def apply_employee_national_id_file_policy_on_create(doc, method):
    """
    File.before_insert for Employee.national_id_scan:
      - force private
      - enforce allowed MIME/ext
    """
    if (
        doc.attached_to_doctype == "Employee"
        and doc.attached_to_field == "national_id_scan"
    ):
        doc.is_private = 1
        fn = (getattr(doc, "file_name", None) or "").lower()
        mime = getattr(doc, "mime_type", None)
        mime_ok = (mime in ALLOWED_MIME) if mime else False
        ext_ok  = fn.endswith(ALLOWED_EXT)
        if not (mime_ok or ext_ok):
            frappe.throw(_("Only PDF, JPG, JPEG, or PNG is allowed for National ID Scan."))

