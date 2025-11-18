import frappe

def execute():
    designations = [
        "مسئول مالی",
        "امور بازرگانی",
        "مسئول فنی",
        "مدیر عامل",
        # add all other unique titles you used in the CSV
    ]

    for d in designations:
        if d and not frappe.db.exists("Designation", d):
            frappe.get_doc({
                "doctype": "Designation",
                "designation_name": d
            }).insert(ignore_permissions=True)
