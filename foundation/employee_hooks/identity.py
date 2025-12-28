# caspian_hr/hr/employee/identity.py
import re
import frappe
from frappe import _

NAT_ID_FIELD = "custom_national_code"




def enforce_business_keys(doc, method=None):
    """Normalize nat_id, enforce mandatory, enforce uniqueness on create."""
    nat = doc.get(NAT_ID_FIELD)
    doc.set(NAT_ID_FIELD, nat)

    if not nat:
        frappe.throw(_("کد ملی الزامی است."))

    if frappe.db.exists("Employee", {NAT_ID_FIELD: nat}):
        frappe.throw(_("این کد ملی قبلاً ثبت شده است."))

def recheck_uniqueness(doc, method=None):
    """Re-normalize and re-check uniqueness during validate (pre-insert edits)."""
    nat = doc.get(NAT_ID_FIELD)
    doc.set(NAT_ID_FIELD, nat)

    if not nat:
        frappe.throw(_("کد ملی الزامی است."))

    exists = frappe.db.get_value("Employee", {NAT_ID_FIELD: nat}, "name")
    if exists and exists != doc.name:
        frappe.throw(_("این کد ملی قبلاً ثبت شده است."))
