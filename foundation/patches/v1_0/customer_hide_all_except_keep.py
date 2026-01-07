import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

DOCTYPE = "Customer"

# Fields to KEEP visible (hidden = 0). Everything else => hidden = 1
KEEP = {
    "territory",
    "customer_name",
    "customer_type",
    "custom_customer_code",
    "custom_tier",
    "custom_legal_form",
    "customer_group",
    "payment_terms",
    "custom_expected_annual_revenue",
    "tax_id"
    "custom_customer_medical_profile",
    "custom_medical_packaging_row",
    "custom_sla_contract",
    "custom_loyalty_program",
    "customer_primary_address",
    "primary_address",
    "customer_primary_contact",
    "custom_whatsapp_number"
    "mobile_no",
    "email_id",
    "custom_site_hse_contact",
    "custom_site_hse_mobile",
    "custom_sites",
    "custom_sites_count",
    "default_currency",
    "default_bank_account",
    "default_price_list"
    "custom_site_hse_contact",
    "custom_site_hse_mobile",
    "custom_waste_pattern",
    "custom_service_window",
    "custom_customer_logo",
    "custom_qr_code",
    "default_price_list"
}

KEEP_BREAK = {
    "basic_info", # Section
    "defaults_tab",# Section
    "primary_address_and_contact_detail",# Section
    "more_info" # Section
}

# Layout fields should not be hidden (it breaks the form layout)
SKIP_FIELDTYPES = {
    "Column Break",
    "Tab Break",
    "HTML",
    "Fold",
    "Heading",
    "Page Break",
}



def execute():
    meta = frappe.get_meta(DOCTYPE)

    for df in meta.fields:
        
        if df.fieldtype in SKIP_FIELDTYPES:
            hidden_value = 0

        # Some section breaks are in KEEP so this if comes second
        # NEVER hide mandatory fields
        if df.reqd:
            hidden_value = 0
        elif df.fieldname in KEEP or df.fieldname in KEEP_BREAK:
            hidden_value = 0 
        else:
            hidden_value = 1

        make_property_setter(
            doctype=DOCTYPE,
            fieldname=df.fieldname,
            property="hidden",
            value=hidden_value,
            property_type="Check",
            for_doctype=False,
        )
