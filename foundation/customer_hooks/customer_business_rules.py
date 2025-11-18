import frappe

def _tier_from_medical(revenue):
    r = (revenue or 0) * 1.0
    if r < 20_000_000: return "Small"
    if r < 50_000_000: return "Mid-Low"
    if r < 100_000_000: return "Mid-High"
    if r < 500_000_000: return "Large"
    return "Key"

def _tier_from_industrial(revenue):
    r = (revenue or 0) * 1.0
    if r <= 50_000_000: return "Small"
    if r <= 150_000_000: return "Mid-Low"
    if r <= 300_000_000: return "Mid-High"
    if r <= 600_000_000: return "Large"
    return "Key"

def _has_rows(doc, tablefield):
    return bool(getattr(doc, tablefield, []) and len(getattr(doc, tablefield)))

def validate_customer_business_rules(doc, _=None):
    dom = (doc.get("customer_domain") or "").strip()

    # --- Auto-tier from domain + expected_annual_revenue ---
    rev = doc.get("expected_annual_revenue") or 0
    if rev < 0:
        frappe.throw("رقم درآمد سالانه نمی‌تواند منفی باشد.")
    if dom == "Medical":
        doc.custom_tier = _tier_from_medical(rev)
    elif dom == "Industrial":
        doc.custom_tier = _tier_from_industrial(rev)

    # --- Service windows: Medical only ---
    if dom == "Medical":
        if not _has_rows(doc, "service_windows"):
            frappe.throw("«پنجره زمانی سرویس» برای پسماند پزشکی الزامی است (شیفت صبح/عصر را مشخص کنید).")

    # --- Sites count (read-only snapshot) ---
    if doc.custom_sites:
        doc.custom_sites_count = len(getattr(doc, "custom_sites") or [])


    # --- Waste pattern cadence by domain ---
    if _has_rows(doc, "custom_waste_pattern"):
        for row in doc.custom_waste_pattern:
            period = (row.frequency_unit or "").strip()
            if dom == "Medical" and period != "Week":
                frappe.throw("در حوزه پزشکی، «الگوی تولید پسماند» باید هفتگی (Week) باشد.")
            if dom == "Industrial" and period != "Month":
                frappe.throw("در حوزه صنعتی، «الگوی تولید پسماند» باید ماهانه (Month) باشد.")
