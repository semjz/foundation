import frappe 

def create_user_and_permission(doc, method=None):
    """
    Employee hook:
    - If user_id is already set: just ensure Company User Permission.
    - If user_id is empty: create/reuse a User from email, set user_id, add permission.
    """

    # 0) If Employee already has a user_id, do NOT create another user.
    if getattr(doc, "user_id", None):
        user_name = doc.user_id

        # Ensure Company permission exists
        if doc.company and not frappe.db.exists(
            "User Permission",
            {"user": user_name, "allow": "Company", "for_value": doc.company},
        ):
            perm = frappe.get_doc({
                "doctype": "User Permission",
                "user": user_name,
                "allow": "Company",
                "for_value": doc.company,
                "apply_to_all_doctypes": 1,
            })
            perm.flags.ignore_permissions = True
            perm.insert()

        # Nothing else to do in this case
        return

    # 1) Get email from company or personal
    email = (doc.company_email or "").strip() or (doc.personal_email or "").strip()

    # 2) Enforce that we have an email
    if not email:
        # This will stop the import for this row with a clear message
        frappe.throw(
            f"Employee {doc.name} has no email (company_email or personal_email). "
            "Each employee must have a unique email so a User can be created."
        )

    # 3) Check if a user already exists with this email
    user_name = frappe.db.get_value("User", {"email": email})
    if user_name:
        # Optional: ensure this user isn't already linked to another Employee
        other_emp = frappe.db.get_value(
            "Employee",
            {"user_id": user_name, "name": ["!=", doc.name]},
            "name",
        )
        if other_emp:
            frappe.throw(
                f"Email {email} is already used by Employee {other_emp}. "
                "Each employee must have a unique email."
            )
        user = frappe.get_doc("User", user_name)
    else:
        # 4) Create user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": doc.employee_name,
            "enabled": 1,
            "new_password": email,
            "user_type": "System User",
            "send_welcome_email": 0,
        })
        user.flags.ignore_permissions = True
        user.insert()
        user_name = user.name

    # 5) Link user to employee (only if field exists and not already set)
    if hasattr(doc, "user_id") and not doc.user_id:
        doc.db_set("user_id", user_name)

    # 6) Only create permission if company is present
    if doc.company:
        if not frappe.db.exists("User Permission", {
            "user": user_name,
            "allow": "Company",
            "for_value": doc.company,
        }):
            perm = frappe.get_doc({
                "doctype": "User Permission",
                "user": user_name,
                "allow": "Company",
                "for_value": doc.company,
                "apply_to_all_doctypes": 1
            })
            perm.flags.ignore_permissions = True
            perm.insert()
    else:
        frappe.log_error(
            f"No company for Employee {doc.name}, skipping User Permission",
            "create_user_and_permission",
        )
