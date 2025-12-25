import frappe

def execute():
    # If Gender doctype doesn't exist (e.g. app not installed), just skip.
    if not frappe.db.table_exists("Gender"):
        return

    allowed_labels = ["Male", "Female"]
    keep_names: list[str] = []

    # Ensure Male / Female exist (by label), record their names so we can keep them
    for label in allowed_labels:
        existing = frappe.get_all(
            "Gender",
            filters={"gender": label},
            pluck="name",
            limit=1,
        )

        if existing:
            name = existing[0]
            keep_names.append(name)
        else:
            # Create new Gender row
            doc = frappe.get_doc({
                "doctype": "Gender",
                "gender": label,
            })
            doc.insert(ignore_permissions=True)
            keep_names.append(doc.name)

    # Delete any Gender records that are NOT Male / Female
    if keep_names:
        to_delete = frappe.get_all(
            "Gender",
            filters={"name": ["not in", keep_names]},
            pluck="name",
        )
    else:
        # (paranoid fallback: if something went wrong above)
        to_delete = frappe.get_all("Gender", pluck="name")

    for name in to_delete:
        frappe.delete_doc(
            "Gender",
            name,
            ignore_permissions=True,
            force=1,  # in case there are links, still delete
        )

    frappe.db.commit()
