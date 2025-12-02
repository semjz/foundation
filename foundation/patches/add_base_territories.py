import frappe

def execute():
    parent_label = "All Territories"

    # Territories you want: (label, SS code)
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

    # 1) Ensure parent territory exists and get its REAL name (primary key)
    parent_name = frappe.db.get_value("Territory", {"territory_name": parent_label}, "name")
    if not parent_name:
        parent_doc = frappe.get_doc({
            "doctype": "Territory",
            "territory_name": parent_label,
            "is_group": 1,
        })
        parent_doc.insert()
        parent_name = parent_doc.name

    # 2) For each city, ensure Territory exists and then create SS mapping
    for label, ss in terrs:
        # find territory by label, get its REAL name
        territory_name = frappe.db.get_value("Territory", {"territory_name": label}, "name")

        if not territory_name:
            terr_doc = frappe.get_doc({
                "doctype": "Territory",
                "territory_name": label,
                "parent_territory": parent_name,
                "is_group": 0,
            })
            terr_doc.insert()
            territory_name = terr_doc.name  # this is what the Link field will store

        # now territory_name is guaranteed to be a valid Territory.name
        # create SS mapping if not exists
        if not frappe.db.exists("Territory SS Code", {"territory": territory_name}):
            ss_doc = frappe.get_doc({
                "doctype": "Territory SS Code",
                "territory": territory_name,  # <-- USE REAL NAME, NOT LABEL
                "ss_code": ss,
            })
            ss_doc.insert()
