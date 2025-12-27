import frappe

# change these to the actual fieldnames you want gone
FIELDS_TO_DELETE = [
    ("Employee", "custom_jalali_date_of_joining"),   # example
    ("Employee", "custom_jalali_contract_end_date_"),  # example
]

def execute():
    # Delete Custom Field docs
    for dt, fieldname in FIELDS_TO_DELETE:
        frappe.db.delete("Custom Field", {"dt": dt, "fieldname": fieldname})

    # Also nuke any hidden/perm property setters for those fields, just in case
    for _, fieldname in FIELDS_TO_DELETE:
        frappe.db.delete(
            "Property Setter",
            {"doc_type": "Employee", "field_name": fieldname}
        )

    frappe.clear_cache(doctype="Employee")
