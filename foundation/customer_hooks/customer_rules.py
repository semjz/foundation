import frappe


def _has_rows(doc, tablefield):
    return bool(getattr(doc, tablefield, []) and len(getattr(doc, tablefield)))

def validate_by_tier(doc, _):

    if tier:
        if not doc.tax_id:
            frappe.throw("شناسه مالیاتی برای Tier=Medium/Large/Key الزامی است.")
        if not (doc.custom_site_hse_contact and doc.custom_site_hse_mobile):
            frappe.throw("نام و موبایل مسئول HSE برای Tier=Medium/Large/Key الزامی است.")
        if not _has_rows(doc, "custom_waste_pattern"):
            frappe.throw("حداقل یک ردیف «الگوی تولید پسماند» لازم است.")

    if tier in ("Large","VIP"):
        
        if not doc.custome_sla_contract: frappe.throw("قرارداد SLA لازم است.")
