import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

DOCTYPE = "Employee"

# Fields to KEEP visible (hidden = 0). Everything else => hidden = 1
KEEP = {
    "first_name",
    "last_name",
    "custom_father_name",
    "gender",
    "date_of_birth"
    "custom_territory",
    "custom_national_code",
    "custom_national_card_scan",
    "gender",
    "date_of_birth",
    "cell_number",
    "personal_email",
    "current_address",
    "image",
    "family_background",
    "blood_group",
    "custom_weight",
    "custom_height",
    "custom_allergies",
    "person_to_be_contacted",
    "emergency_phone_number",
    "relation",
    "user_id",
    "create_user",
    "create_user_permission",
    "custom_canonical_id",
    "designation",
    "date_of_joining",
    "status",
    "internal_work_history",
    "custom_company_province",
    "custom_jalali_contract_end_date_",
    "education",
    "custom_latest_qualification_scan",
    "custom_contract_type",
    "contract_end_date"
    "custom_contract_scan_",

    "company",
    "custom_company_province"
    "bank_name",
    "bank_ac_no",
    "custom_shaba_no",
    "custom_payroll_missing_fields",
    "custom_payroll_enabled",
    "custom_payroll_enabled_on",

}

KEEP_BREAK = {
    "basic_information", # Section
    "erpnext_user", # Section
    "custom_health_info",# Section
    "custom_emergency_contact_info",# Section
    "custom_employement_details",# Section
    "custom_contract_info",# Section
    "bank_details_section"# Section
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
