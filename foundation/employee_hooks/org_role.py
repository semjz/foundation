# replace previous org_role module with this
import frappe
from frappe import _

ORG_TRACK_FIELD = "custom_org_track"       # Select: Administrative\nField (custom field)
DESIGNATION_FIELD = "designation"   # Core ERPNext field: Link -> Designation

ALLOWED_TRACKS = {"Administrative", "Field"}

logger = frappe.logger("org_role", allow_site=True)

def require_org_role_fields(doc, method=None):
    track = (doc.get(ORG_TRACK_FIELD) or "").strip()
    desg  = (doc.get(DESIGNATION_FIELD) or "").strip()

    logger.info(f"[Employee Validate] name={doc.name} track='{track}' designation='{desg}'")
    
    if not track:
        frappe.throw(_("org_track اجباری است (Administrative یا Field)."))
    if track not in ALLOWED_TRACKS:
        frappe.throw(_("org_track فقط می‌تواند Administrative یا Field باشد."))
    if not desg:
        frappe.throw(_("Designation اجباری است."))

