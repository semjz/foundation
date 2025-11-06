import frappe

def create_user_and_permission(doc, method=None):
    email = doc.company_email or doc.personal_email
    if not email:
        return

    # Check if user exists
    user_name = frappe.db.get_value("User", {"email": email})
    if not user_name:
        # Create user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": doc.employee_name,
            "enabled": 1
        })
        user.flags.ignore_permissions = True
        user.insert()
        user_name = user.name

    # Link user to employee
    doc.db_set("user_id", user_name)

    # Check if permission already exists
    if not frappe.db.exists("User Permission", {
        "user": user_name,
        "allow": "Company",
        "for_value": doc.company
    }):
        # Create permission
        frappe.get_doc({
            "doctype": "User Permission",
            "user": user_name,
            "allow": "Company",
            "for_value": doc.company
        }).insert(ignore_permissions=True)
