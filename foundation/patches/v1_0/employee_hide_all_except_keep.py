import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

DOCTYPE = "Employee"

# Fields to KEEP visible (hidden = 0). Everything else => hidden = 1
KEEP = {
    "first_name",
    "middle_name",
    "last_name",
    "employee_name",
    "custom_custom_father_name",
    "custom_custom_territory",
    "custom_custom_canonical_id",
    "gender",
    "date_of_birth",
    "date_of_joining",
    "custom_org_track",
    "custom_employee_no",
    "custom_contract_type",
    "image",
    "status",
    "user_id",
    "create_user",
    "create_user_permission",
    "company",
    "custom_company_province",
    "department",
    "designation",
    "contract_end_date",
    "custom_jalali_contract_end_date_",
    "cell_number",
    "personal_email",
    "custom_jalali_date_of_joining",
    "prefered_email",
    "current_address",
    "person_to_be_contacted",
    "emergency_phone_number",
    "relation",
    "bank_name",
    "bank_ac_no",
    "custom_shaba_no",
    "blood_group",
    "health_details",
    "custom_national_code",
    "custom_national_card_scan",
    "education",
    "custom_latest_qualification_scan",
}

# Layout fields should not be hidden (it breaks the form layout)
SKIP_FIELDTYPES = {
    "Section Break",
    "Column Break",
    "Tab Break",
    "HTML",
    "Fold",
    "Heading",
    "Page Break",
}

# System/meta fields
SYSTEM_FIELDS = {
    "name",
    "owner",
    "creation",
    "modified",
    "modified_by",
    "docstatus",
    "idx",
}

def execute():
    meta = frappe.get_meta(DOCTYPE)

    for df in meta.fields:
        if df.fieldtype in SKIP_FIELDTYPES:
            continue
        if df.fieldname in SYSTEM_FIELDS:
            continue

        # 🚫 NEVER hide mandatory fields
        if df.reqd:
            hidden_value = 0
        else:
            hidden_value = 0 if df.fieldname in KEEP else 1

        make_property_setter(
            doctype=DOCTYPE,
            fieldname=df.fieldname,
            property="hidden",
            value=hidden_value,
            property_type="Check",
            for_doctype=False,
        )
