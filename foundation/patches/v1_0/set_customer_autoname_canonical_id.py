import frappe

def execute():
    frappe.db.set_value("DocType", "Customer", "autoname", "field:canonical_id")
