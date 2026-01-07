# foundation/patches/v1_3/enable_mobile_login_using_mobile_no.py

import frappe
from frappe.utils import cint

def execute():
    # Read current value (0/1) of the checkbox
    current = cint(
        frappe.db.get_single_value(
            "System Settings", "allow_login_using_mobile_number"
        ) or 0
    )

    # If already enabled, nothing to do
    if current:
        return

    # Turn on "Allow Login using Mobile Number"
    frappe.db.set_value(
        "System Settings",
        "System Settings",
        "allow_login_using_mobile_number",
        1,
    )

    # Make sure changes are visible in login page / cache
    frappe.clear_cache()
