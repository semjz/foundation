import frappe

ROLES_TO_ENSURE = [
    {"role_name": "Ops Manager", "desk_access": 1},
    {"role_name": "Finance", "desk_access": 1},
]

def execute():
    for role_def in ROLES_TO_ENSURE:
        _ensure_role(role_def)


def _ensure_role(role_def: dict):
    name = role_def["role_name"]

    # If role already exists, you can optionally update some fields
    if frappe.db.exists("Role", name):
        role = frappe.get_doc("Role", name)
        # for safety, only update what you really care about:
        role.desk_access = role_def.get("desk_access", role.desk_access)
        role.save()
        return

    # If not, create it
    role = frappe.get_doc({
        "doctype": "Role",
        "role_name": name,
        "desk_access": role_def.get("desk_access", 1),
    })
    role.insert(ignore_permissions=True)
