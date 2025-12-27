import frappe

def execute():
    try:
        frappe.db.set_value("HR Settings", None, "emp_created_by", "Employee Number")
        frappe.clear_cache(doctype="Employee")
    except Exception:
        frappe.log_error("Failed to set HR Settings.emp_created_by")
