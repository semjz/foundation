import frappe

def execute():
    parent = "All Territories"

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

    # ensure parent exists
    if not frappe.db.exists("Territory", parent):
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": parent,
            "is_group": 1,
        }).insert()

    for name, ss in terrs:
        if not frappe.db.exists("Territory", name):
            doc = frappe.get_doc({
                "doctype": "Territory",
                "territory_name": name,
                "parent_territory": parent,
                "is_group": 0,
            })
            doc.insert()

        if not frappe.db.exists("Territory SS Code", {"territory": name}):
            frappe.get_doc({
                "doctype": "Territory SS Code",
                "territory": name,
                "ss_code": ss,
            }).insert()
