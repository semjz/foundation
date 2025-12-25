import frappe

def execute():
    terrs = [
        ("Mashhad", "MS"),
        ("Qazvin", "QZ"),
        ("Zanjan", "ZN"),
        ("Shiraz", "SH"),
        ("Semnan", "SN"),
        ("Abhar", "AB"),
        ("Tehran", "TH"),
        ("Chalous", "CH"),
    ]

    for name, ss in terrs:
        if frappe.db.exists("Territory", name):
            # Convert existing territory to a ROOT node
            frappe.db.set_value(
                "Territory",
                name,
                {
                    "parent_territory": "",
                    "is_group": 0,
                },
            )
        else:
            # Create as root territory with no parent
            frappe.get_doc({
                "doctype": "Territory",
                "territory_name": name,
                "parent_territory": "",
                "is_group": 0,
            }).insert()

        # Ensure SS Code exists for this territory
        if not frappe.db.exists("Territory SS Code", {"territory": name}):
            frappe.get_doc({
                "doctype": "Territory SS Code",
                "territory": name,
                "ss_code": ss,
            }).insert()
