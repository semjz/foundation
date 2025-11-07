# foundation/customer_hooks/portal.py
import frappe

EMAIL_FIELDS = ("primary_email", "email_id")

def _get_email(doc):
    for f in EMAIL_FIELDS:
        if doc.get(f):
            return doc.get(f).strip()
    return None

def ensure_user_and_permission(doc, method=None):
    email = _get_email(doc)
    if not email:
        return

    # 1) Ensure Website User exists
    user_name = frappe.db.get_value("User", {"email": email})
    if not user_name:
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": doc.customer_name or email.split("@")[0],
            "enabled": 1,
            "user_type": "Website User",
            "roles": [{"role": "Customer"}]
        })
        user.flags.ignore_permissions = True
        user.insert()
        user_name = user.name

    # 2) Ensure User Permission: allow only THIS Customer
    if not frappe.db.exists("User Permission", {
        "user": user_name, "allow": "Customer", "for_value": doc.name
    }):
        frappe.get_doc({
            "doctype": "User Permission",
            "user": user_name,
            "allow": "Customer",
            "for_value": doc.name,
            "apply_to_all_doctypes": 0
        }).insert(ignore_permissions=True)
