# foundation/tests/test_multi_company_permission.py

from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch
import frappe
import random, string

# ----------------- small speed helpers -----------------

def _rand(n=6):
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=n))

def _digits(n=10):
    return "".join(random.choice("0123456789") for _ in range(n))

def _fast_company(name):
    """Create a minimal Company via db_insert() to avoid on_update heavy flows."""
    if frappe.db.exists("Company", name):
        return name
    doc = frappe.get_doc({"doctype": "Company"})
    doc.company_name = name
    if any(f.fieldname == "abbr" for f in doc.meta.fields):
        doc.abbr = (name[:3] or "CMP").upper()
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_validate = True
    doc.flags.ignore_permissions = True
    doc.db_insert()  # <-- no COA/tax wizard
    return name

def _ensure_designation(name="Truck Driver 6T"):
    if not frappe.db.exists("Designation", name):
        d = frappe.get_doc({"doctype": "Designation", "designation_name": name})
        d.flags.ignore_permissions = True
        d.db_insert()
    return name

# ----------------- the test -----------------

class TestEmployeeUserPermission(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # strict user permissions globally
        frappe.db.set_single_value("System Settings", "strict_user_permissions", 1)
        frappe.clear_cache()

        # create two lightweight companies once
        cls.company_a = _fast_company(f"UnitTest Co A {_rand(4)}")
        cls.company_b = _fast_company(f"UnitTest Co B {_rand(4)}")

        _ensure_designation()

    def setUp(self):
        frappe.flags.in_test = True
        frappe.flags.mute_emails = True
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.set_user("Administrator")

    def _new_employee(self, *, company, email, custom_national_code=None):
        emp = frappe.new_doc("Employee")
        emp.first_name = "Test"
        emp.company = company
        emp.company_email = email
        emp.org_track = "Administrative"
        emp.designation = "Truck Driver 6T"

        # give each employee a unique custom_national_code (satisfies your identity hook)
        emp.custom_national_code = custom_national_code or _digits(10)

        # speed/escape hatches
        emp.flags.ignore_mandatory = True     # bypass unrelated schema mandatories
        emp.flags._skip_id_scan = True        # bypass national_id_scan policy in tests
        emp.name = f"TEST-EMP-{_rand(8)}"     # stable name avoids autoname queries

        emp.insert(ignore_permissions=True)   # let your hooks run (create user/perm)
        return emp

    def test_employee_user_permission(self):
        # Patch heavy email sending so User insert stays fast
        from frappe.core.doctype.user.user import User
        def _noop(*a, **k): return None

        with patch.object(User, "send_password_notification", _noop), \
             patch.object(User, "send_welcome_mail_to_user", _noop), \
             patch.object(User, "send_login_mail", _noop), \
             patch("frappe.sendmail", _noop):

            # Employee in Company A (hook should create user + company permission)
            email_a = f"{_rand(6)}@example.com"
            emp_a = self._new_employee(company=self.company_a, email=email_a)

            user_name = frappe.db.get_value("User", {"email": email_a}, "name")
            self.assertIsNotNone(user_name)
            self.assertEqual(emp_a.user_id, user_name)

            self.assertTrue(
                frappe.db.exists(
                    "User Permission",
                    {"user": user_name, "allow": "Company", "for_value": self.company_a},
                )
            )

            # Another employee in Company B (different custom_national_code)
            email_b = f"{_rand(6)}@example.com"
            emp_b = self._new_employee(company=self.company_b, email=email_b)

            # Switch to restricted user (company A)
            frappe.set_user(user_name)

            # 1) List API must not show company B employee
            rows = frappe.get_list(
                "Employee",
                filters={"name": emp_b.name},
                pluck="name",
                ignore_permissions=False,
            )
            self.assertEqual(rows, [])

            # 2) Explicit permission check must fail
            from frappe.exceptions import PermissionError
            with self.assertRaises(PermissionError):
                frappe.get_doc("Employee", emp_b.name).check_permission("read")

            # sanity: own employee row is visible
            rows_a = frappe.get_list(
                "Employee",
                filters={"name": emp_a.name},
                pluck="name",
                ignore_permissions=False,
            )
            self.assertEqual(rows_a, [emp_a.name])
