# foundation/customer_tier_rules.py
import frappe
from frappe import _

TIER_FIELD = "custom_tier"
frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("tier", allow_site=True)

def enforce_customer_tier_rules(doc, method=None):
    # dump a lot of info
    logger.info(
        f"[TierRules] name={getattr(doc, 'name', None)} "
        f"tier_field={TIER_FIELD!r} "
        f"doc.get(TIER_FIELD)={doc.get(TIER_FIELD)!r} "
        f"doc.flags.ignore_mandatory = {doc.flags.ignore_mandatory} "
        f"custom_tier_attr={getattr(doc, 'custom_tier', None)!r} "
        f"keys={list(doc.as_dict().keys())}"
    )


    tier = doc.get(TIER_FIELD)

    missing = []
    if tier in ["Small", "Mid-Low", "Mid-High"]:
        if not doc.tax_id:
            missing.append(_("Tax ID"))
        if not doc.custom_site_hse_contact:
            missing.append(_("Site HSE Contact"))
        if not doc.custom_site_hse_mobile:
            missing.append(_("Site HSE Mobile"))
        if not doc.custom_waste_pattern:
            missing.append(_("Waste Pattern"))

    if tier in ("Large", "VIP") and not doc.custom_service_windows:
        missing.append(_("Service Window(s)"))

    if missing and not doc.flags.ignore_tier_mandatory:
        msg = _("For tier {0}, the following fields are required: {1}").format(
            tier, ", ".join(missing)
        )
        raise frappe.ValidationError(msg)
