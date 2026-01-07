import frappe


def execute():
    """
    One-time patch:
    For all enabled Users that have a mobile_no,
    set username = cleaned mobile_no.
    Assumes mobile_no is already unique at DB level.
    """

    users = frappe.get_all(
        "User",
        filters={"enabled": 1, "mobile_no": ["is", "set"]},
        fields=["name", "mobile_no"],
    )

    if not users:
        return

    for u in users:
        mobile = (u.mobile_no or "").strip().replace(" ", "")
        if not mobile:
            continue

        frappe.db.set_value(
            "User",
            u.name,
            "username",
            mobile,
            update_modified=False,
        )

    frappe.db.commit()
