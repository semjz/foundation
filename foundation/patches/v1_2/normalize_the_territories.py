import frappe

ROOT = "CIE Territories"       # or "CIE Territories" if you prefer
TERRS = [
    ("Mashhad", "MS"),
    ("Qazvin", "QZ"),
    ("Tehran", "TH"),
]


def execute():
    # 1) Ensure root exists and is a group at the top level
    if frappe.db.exists("Territory", ROOT):
        frappe.db.set_value(
            "Territory",
            ROOT,
            {
                "parent_territory": "",
                "is_group": 1,
            },
        )
    else:
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": ROOT,
            "parent_territory": "",
            "is_group": 1,
        }).insert()

    # 2) Ensure each of your territories exists as a leaf under the root
    for name, ss in TERRS:
        if frappe.db.exists("Territory", name):
            frappe.db.set_value(
                "Territory",
                name,
                {
                    "parent_territory": ROOT,
                    "is_group": 0,
                },
            )
        else:
            frappe.get_doc({
                "doctype": "Territory",
                "territory_name": name,
                "parent_territory": ROOT,
                "is_group": 0,
            }).insert()

        # 3) Ensure Territory SS Code exists
        if not frappe.db.exists("Territory SS Code", {"territory": name}):
            frappe.get_doc({
                "doctype": "Territory SS Code",
                "territory": name,
                "ss_code": ss,
            }).insert()
