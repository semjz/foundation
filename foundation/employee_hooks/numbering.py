# caspian_hr/hr/employee/numbering.py
import frappe
from frappe.model.naming import make_autoname

EMP_NO_FIELD = "employee_no"

province_to_code = {"تهران":"TEH",
                    "مشهد":"MHD",
                    "قزوین":"Qaz"}

def get_province_code(province) -> str:
    return province_to_code[province]
    

def _series_key(doc) -> str:
    company_code = (getattr(doc, "company_code", None) or "SMW").upper()
    province3    = get_province_code(getattr(doc, "custom_company_province", None) or "TEH").upper()
    # الگوی چهاررقمی: .####  (مثل 0001, 0002, ...)
    return f"EMP-{company_code}-{province3}-" + ".####"

def assign_employee_display_number(doc, method=None):
    """تولید employee_no یک‌بار برای همیشه (ثابت و انسان‌خوان)."""
    if not doc.get(EMP_NO_FIELD):
        doc.set(EMP_NO_FIELD, make_autoname(_series_key(doc)))
