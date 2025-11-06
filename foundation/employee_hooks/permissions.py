def set_user_permission(doc, method=None):
    if not getattr(doc.flags, "user_created", False):
        return  # ✅ Skip if user wasn't just created
    
    user = doc.user_id
    if not user:
        return
    
    doctype = "Company"  # or derive from context
    for_value = doc.company  # example field
    is_default = 1
    applicable_for = None
    hide_descendants = 0

    user_permission = frappe.get_doc({
        "doctype": "User Permission",
        "user": user,
        "allow": doctype,
        "for_value": for_value,
        "is_default": is_default,
        "applicable_for": applicable_for,
        "apply_to_all_doctypes": 0 if applicable_for else 1,
        "hide_descendants": hide_descendants
    })
    user_permission.insert(ignore_permissions=True)
