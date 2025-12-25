# replace previous org_role module with this
import frappe
from frappe import _

DESIGNATION_FIELD = "designation"   # Core ERPNext field: Link -> Designation

ALLOWED_TRACKS = {"Administrative", "Field"}

logger = frappe.logger("org_role", allow_site=True)

def require_org_role_fields(doc, method=None):
    desg  = (doc.get(DESIGNATION_FIELD) or "").strip()

    if not desg:
        frappe.throw(_("Designation اجباری است."))

