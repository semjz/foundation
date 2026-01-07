# foundation/customer_hooks/portal.py

import frappe

EMAIL_FIELDS = ("primary_email", "email_id")

def _get_email(doc):
    # Try all known email fields on the Customer
    for f in EMAIL_FIELDS:
        val = doc.get(f)
        if val:
            return val.strip()
    return None

def _generate_dummy_email(doc):
    """Generate a deterministic dummy email for this customer."""
    # Prefer a stable, unique field
    base = doc.get("custom_canonical_id")
    # Remove spaces just to be safe
    base = str(base).replace(" ", "")
    return f"cust-{base}@dummy.local"

def ensure_user_and_permission(doc, method=None):
    # 1) Get email from the document, or generate a dummy one
    email = _get_email(doc)
    if not email:
        email = _generate_dummy_email(doc)
        # Optionally persist it on the Customer so you can see it later
        doc.email_id = email
        # Use db_set so we don't trigger full validation again
        frappe.db.set_value(doc.doctype, doc.name, "email_id", email)

    # 2) Ensure Website User exists
    user_name = frappe.db.get_value("User", {"email": email})
    if not user_name:
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": doc.customer_name or email.split("@")[0],
            "enabled": 1,
            "user_type": "Website User",
            "roles": [{"role": "Customer"}],
        })
        user.flags.ignore_permissions = True
        user.insert()
        user_name = user.name

    # 3) Ensure User Permission: allow only THIS Customer
    if not frappe.db.exists(
        "User Permission",
        {"user": user_name, "allow": "Customer", "for_value": doc.name},
    ):
        frappe.get_doc({
            "doctype": "User Permission",
            "user": user_name,
            "allow": "Customer",
            "for_value": doc.name,
            "apply_to_all_doctypes": 0,
        }).insert(ignore_permissions=True)
