import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

EMP = "Employee"

def execute():
    # Date of Joining: visible, required, not read-only, permlevel 0
    try:
        make_property_setter(EMP, "date_of_joining", "hidden", 0, "Check")
        make_property_setter(EMP, "date_of_joining", "reqd", 1, "Check")
        make_property_setter(EMP, "date_of_joining", "read_only", 0, "Check")
        make_property_setter(EMP, "date_of_joining", "permlevel", 0, "Int")
    except Exception:
        frappe.log_error("Failed to normalize Employee.date_of_joining")

    # Internal Work History: visible, permlevel 0
    try:
        make_property_setter(EMP, "internal_work_history", "hidden", 0, "Check")
        make_property_setter(EMP, "internal_work_history", "permlevel", 0, "Int")
    except Exception:
        frappe.log_error("Failed to normalize Employee.internal_work_history")

    frappe.clear_cache(doctype=EMP)
