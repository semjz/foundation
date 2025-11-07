import frappe

def _has_rows(doc, tablefield):
    return bool(getattr(doc, tablefield, []) and len(getattr(doc, tablefield)))

def validate_by_tier(doc, _):
    tier = (doc.custom_tier or "").strip()

    if tier in ("Medium","Large","Key"):
        if not doc.tax_id:
            frappe.throw("شناسه مالیاتی برای Tier=Medium/Large/Key الزامی است.")
        if not (doc.site_hse_contact and doc.site_hse_mobile):
            frappe.throw("نام و موبایل مسئول HSE برای Tier=Medium/Large/Key الزامی است.")
        if not _has_rows(doc, "waste_pattern"):
            frappe.throw("حداقل یک ردیف «الگوی تولید پسماند» لازم است.")

    if tier in ("Large","Key"):
        if not _has_rows(doc, "service_windows"):
            frappe.throw("برای Tier=Large/Key حداقل یک «پنجره زمانی سرویس» لازم است.")
        # Optional strict rules:
        # if not doc.sla_contract: frappe.throw("قرارداد SLA لازم است.")
