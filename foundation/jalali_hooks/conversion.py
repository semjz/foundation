import frappe
import jdatetime
from frappe.utils import formatdate

def jalali_to_gregorian(jstr):
    """Convert '1403/01/01' -> '2024-03-20' (ISO date string)"""
    if not jstr:
        return None

    jstr = jstr.strip()
    # expecting jYYYY/jMM/jDD
    y, m, d = map(int, jstr.split("/"))
    g = jdatetime.date(y, m, d).togregorian()
    # Frappe likes 'YYYY-MM-DD'
    return g.strftime("%Y-%m-%d")

def employee_validate(doc, method):
    # Date of Joining
    if getattr(doc, "jalali_date_of_joining", None) and not doc.date_of_joining:
        doc.date_of_joining = jalali_to_gregorian(doc.jalali_date_of_joining)

    # Contract End Date
    if getattr(doc, "jalali_contract_end_date", None) and not doc.contract_end_date:
        doc.contract_end_date = jalali_to_gregorian(doc.jalali_contract_end_date)
