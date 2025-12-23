# foundation/tests/test_employee_payroll_flags.py

import pytest
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, getdate

EMP = "Employee"

# ---- tiny helpers -------------------------------------------------

_MIN_COMPANY = "UnitTest Co"
_MIN_ABBR    = "UTC"

def _ensure_company_fast():
    if frappe.db.exists("Company", _MIN_COMPANY):
        return _MIN_COMPANY
    d = frappe.get_doc({"doctype": "Company"})
    d.company_name = _MIN_COMPANY
    # keep it super light
    if any(f.fieldname == "abbr" for f in d.meta.fields):
        d.abbr = _MIN_ABBR
    d.flags.ignore_mandatory = True
    d.flags.ignore_validate = True
    d.flags.ignore_permissions = True
    d.db_insert()  # skip on_update/COA wizard
    return _MIN_COMPANY

def _ensure_designation(name="Truck Driver 6T"):
    if not frappe.db.exists("Designation", name):
        doc = frappe.get_doc({"doctype": "Designation", "designation_name": name})
        doc.flags.ignore_permissions = True
        doc.db_insert()
    return name

def _new_min_employee(**kw):
    _ensure_company_fast()
    _ensure_designation()

    emp = frappe.new_doc(EMP)
    emp.first_name   = kw.get("first_name", "Ali")
    if "company" in [f.fieldname for f in emp.meta.fields]:
        emp.company = kw.get("company", _MIN_COMPANY)

    # satisfy unrelated hooks (identity/org-role), but skip ID-scan policy
    emp.custom_national_code = kw.get("custom_national_code", "1234567890")
    emp.org_track     = kw.get("org_track", "Administrative")
    emp.designation   = kw.get("designation", "Truck Driver 6T")

    # only bypass schema mandatories; hooks should still run
    emp.flags.ignore_mandatory = True
    emp.flags._skip_id_scan = True

    emp.insert(ignore_permissions=True)
    return emp

# ---- the actual test ----------------------------------------------

class TestEmployeePayrollFlags(FrappeTestCase):

    def test_payroll_flags_toggle_with_required_fields(self):
        # 1) Create Employee WITHOUT required payroll fields
        emp = _new_min_employee()

        # Run validation hook to populate flags on insert (validate runs during insert),
        # but we’ll force a second run to be explicit
        emp.run_method("validate")
        emp.reload()

        # Expect payroll disabled with missing list and no enabled_on
        assert int(emp.custom_payroll_enabled or 0) == 0
        assert (emp.custom_payroll_missing_fields or "").strip() != ""
        assert not emp.custom_payroll_enabled_on

        # 1) Education row
        emp.append("education", {
            "school_univ": "Tehran University",
            "qualification": "BSc",
            "level": "Graduate",
            "year_of_passing": 1399,
            "class_per": "A",
            "maj_opt_subj": "CS",
        })

        # 2) Other required fields (with valid formats)
        emp.passport_number = "A1234567"
        emp.bank_name = "Bank Saman"
        emp.bank_ac_no = "12345678"                         # 6–24 digits
        emp.custom_shaba_no = "IR820540102680020817909002"  # checksum-valid IBAN
        emp.marital_status = "Single"
        emp.person_to_be_contacted = "John Doe"
        emp.emergency_phone_number = "+989121234567"        # +?\d{8,15}
        emp.relation = "Brother"
        emp.custom_contract_type = "Permanent"              # or "Experimental"

        emp.save()
        emp.reload()

        assert int(emp.custom_payroll_enabled or 0) == 1, f"Why disabled: {emp.custom_payroll_missing_fields}"
        assert (emp.custom_payroll_missing_fields or "").strip() == ""
        assert emp.custom_payroll_enabled_on


        assert int(emp.custom_payroll_enabled or 0) == 1

        # missing fields should be empty/None after success
        mf = (emp.custom_payroll_missing_fields or "").strip()
        assert mf == "", f"expected no missing fields, got: {mf}"

        # enabled_on should be set to today (date-only)
        assert emp.custom_payroll_enabled_on, "enabled_on should be set"
        assert getdate(emp.custom_payroll_enabled_on) == getdate(today())
