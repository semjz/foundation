# caspian_hr/hr/employee/immutability.py
import frappe
from frappe import _

IMMUTABLE_FIELDS = ["national_code", "employee_no"]

def lock_immutable_identifiers(doc, method=None):
    """بعد از DocStatus=1 اجازهٔ تغییر nat_id / employee_no نده."""
    if doc.docstatus > 0:
        for field in IMMUTABLE_FIELDS:
            if doc.has_value_changed(field):
                frappe.throw(_("تغییر {0} پس از تایید مجاز نیست.").format(field))
