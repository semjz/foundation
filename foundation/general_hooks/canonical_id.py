import frappe

TERRITORY = "custom_territory"
CANONICAL_ID = "custom_canonical_id"

# Map doctype -> T code
ENTITY_TYPE_MAP = {
    "Customer": "C",
    "Employee": "E",
    # add more when needed:
    # "Supplier": "S",
    # "Driver": "D",
    # "Vehicle": "V",
    # "Project": "P",
    # "Facility": "F",
    # "Route": "R",
    # "Contract": "CT",
}


def get_ss_from_territory(territory_name: str) -> str:
    """Get SS from Territory SS Code mapping."""
    ss_code = frappe.db.get_value(
        "Territory SS Code",
        {"TERRITORY": territory_name},
        "ss_code",
    )

    if not ss_code:
        frappe.throw(
            f"SS code not found for Territory '{territory_name}' in 'Territory SS Code'"
        )

    return ss_code



def set_canonical_id(doc, method=None):
    """
    Hook target:
    - runs on before_insert
    - uses Territory -> Territory SS Code -> ss_code
    - generates: SS-T-NNNNN
    """
    

    # don't overwrite if it's already set (e.g. data import)
    if doc.custom_canonical_id:
        return

    doctype = doc.doctype
    entity_type = ENTITY_TYPE_MAP.get(doctype)
    if not entity_type:
        # not a managed entity type
        return

    territory_name = doc.custom_territory
    if not territory_name:
        frappe.throw(f"Territory is required to generate Canonical ID for {doctype}")

    # 1) SS from Territory SS Code
    ss_code = get_ss_from_territory(territory_name)

    # 2) NNNNN based on how many existing records share this SS + T prefix
    serial_str = doc.custom_sepidar_code

    # 3) Final canonical ID (no K for now)
    doc.custom_canonical_id = f"{ss_code}-{entity_type}-{serial_str}"
