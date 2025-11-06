# replace previous org_role module with this
import frappe
from frappe import _

ORG_TRACK_FIELD = "org_track"       # Select: Administrative\nField (custom field)
DESIGNATION_FIELD = "designation"   # Core ERPNext field: Link -> Designation

ALLOWED_TRACKS = {"Administrative", "Field"}

def require_org_role_fields(doc, method=None):
    """Require org_track (custom) + designation (core) and validate value set."""
    track = (doc.get(ORG_TRACK_FIELD) or "").strip()
    desg  = (doc.get(DESIGNATION_FIELD) or "").strip()

    if not track:
        frappe.throw(_("org_track اجباری است (Administrative یا Field)."))

    if track not in ALLOWED_TRACKS:
        frappe.throw(_("org_track فقط می‌تواند Administrative یا Field باشد."))

    if not desg:
        frappe.throw(_("Designation اجباری است."))
