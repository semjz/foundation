import frappe

@frappe.whitelist()
def territory_leaves_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT name, territory_name
        FROM `tabTerritory`
        WHERE name != 'All Territories'
          AND (name LIKE %(txt)s OR territory_name LIKE %(txt)s)
        ORDER BY territory_name
        LIMIT %(start)s, %(page_len)s
    """, {
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len,
    })
