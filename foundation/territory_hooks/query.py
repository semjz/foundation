import frappe


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def territory_link_query(doctype, txt, searchfield, start, page_len, filters):
    """
    Standard query for Territory Link fields:
    - Always hide group nodes (is_group = 1)
    - Apply any extra filters passed in
    """
    if filters is None:
        filters = {}

    # Always enforce leaf nodes only
    filters = dict(filters)  # copy to avoid mutating original
    filters["is_group"] = 0

    # Basic LIKE search on the chosen field (usually 'name')
    return frappe.db.get_list(
        "Territory",
        filters=filters,
        fields=["name"],
        as_list=True,
        start=start,
        page_length=page_len,
        order_by=f"`{searchfield}` asc",
    )
