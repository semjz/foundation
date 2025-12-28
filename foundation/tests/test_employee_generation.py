# apps/foundation/foundation/tests/test_employee_generation.py

import random

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate


SKIP_FIELDTYPES = {
    "Section Break",
    "Column Break",
    "Tab Break",
    "HTML",
    "Fold",
    "Button",
    "Table",
    "Table MultiSelect",
    "Page Break",
}

# Adjust these if your fieldnames differ
TERRITORY_FIELD = "custom_territory"
NAT_ID_FIELD = "custom_national_code"
SEPIDAR_FIELD = "custom_sepidar_code"


class TestEmployeeGeneration(FrappeTestCase):
    # ------------------ main tests ------------------

    def test_can_create_employee_with_all_required_fields(self):
        """Smoke test: can we create an Employee at all, with current business rules."""
        employee_data = self._build_minimal_employee_data()

        print("EMPLOYEE DATA:", employee_data)
        self.assertIn(NAT_ID_FIELD, employee_data, "national code not populated!")
        self.assertIn(SEPIDAR_FIELD, employee_data, "sepidar code not populated!")

        emp = frappe.get_doc(employee_data)
        emp.insert()
        self.assertTrue(emp.name)

    def test_ops_manager_can_create_employee(self):
        """
        Permission test: a user with Ops Manager role should be able to create Employee.
        This uses the same minimal payload as the smoke test, but under a different user.
        """
        user = self._make_ops_manager_user()

        # Switch session user to Ops Manager
        self.set_user(user.name)

        try:
            employee_data = self._build_minimal_employee_data()

            emp = frappe.get_doc(employee_data)
            emp.insert()

            self.assertTrue(emp.name)
        finally:
            # Always restore so we don't leak user context into other tests
            self.set_user("Administrator")

    # ------------------ data builder ------------------

    def _build_minimal_employee_data(self) -> dict:
        """Build an Employee dict that satisfies all current meta + business rules."""
        meta = frappe.get_meta("Employee")

        employee_data = {
            "doctype": "Employee",
        }

        # Fill based on DocType meta
        for df in meta.fields:
            if not df.reqd:
                continue
            if df.read_only:
                continue
            if df.fieldtype in SKIP_FIELDTYPES:
                continue

            value = self._dummy_value_for_field(df)
            if value is not None:
                employee_data[df.fieldname] = value

        # Hard guarantees for fields your business logic cares about

        # First name
        employee_data["first_name"] = employee_data.get("first_name") or "Test"

        # Company
        employee_data["company"] = (
            employee_data.get("company") or self._get_default_company()
        )

        # National code: must be numeric and unique (identity.py)
        employee_data[NAT_ID_FIELD] = self._generate_unique_national_code()

        # Sepidar code: must be 5-digit and unique (affects autoname)
        employee_data[SEPIDAR_FIELD] = self._generate_unique_sepidar_code()

        # Territory: required for canonical_id hook; do NOT create, just pick one
        employee_data[TERRITORY_FIELD] = employee_data.get(TERRITORY_FIELD) 


        return employee_data

    # ------------------ helpers ------------------

    def _dummy_value_for_field(self, df):
        """Return a simple dummy value based on fieldtype + special-case rules."""

        # National code: special handling to align with identity.py
        if df.fieldname == NAT_ID_FIELD:
            return self._generate_unique_national_code()

        # Sepidar code: 5-digit unique code
        if df.fieldname == SEPIDAR_FIELD:
            return self._generate_unique_sepidar_code()

        # Email fields
        if "email" in (df.fieldname or "").lower():
            return self._generate_unique_email()

        # Mobile / cell number
        if df.fieldname == "cell_number":
            return "09318337753"

        ft = df.fieldtype

        if ft in ("Data", "Small Text", "Long Text"):
            return f"Test {df.fieldname}"

        if ft in ("Int", "Float", "Currency"):
            return 1

        if ft == "Date":
            return nowdate()

        if ft == "Check":
            return 1

        if ft == "Link":
            # IMPORTANT: you must know how to satisfy required links
            return self._get_dummy_link(df.options)

        # For now, ignore anything unknown
        return None

    def _generate_unique_national_code(self) -> str:
        """
        Generate a 10-digit numeric national code that:
        - survives _normalize_nat (digits only)
        - does not already exist in Employee.custom_national_code
        """
        while True:
            nat = f"{random.randint(10_000_000_0, 99_999_999_9)}"
            if not frappe.db.exists("Employee", {NAT_ID_FIELD: nat}):
                return nat

    def _generate_unique_sepidar_code(self) -> str:
        """
        Generate a 5-digit numeric Sepidar code that:
        - is unique on Employee.custom_sepidar_code
        - helps avoid duplicate autoname collisions
        """
        while True:
            code = f"{random.randint(10_000, 99_999)}"  # 5 digits
            if not frappe.db.exists("Employee", {SEPIDAR_FIELD: code}):
                return code

    def _get_dummy_link(self, doctype):
        """Return a valid name for the Link doctype (may auto-create, except Territory)."""

        if not doctype:
            return None

        # Company has its own helper
        if doctype == "Company":
            return self._get_default_company()

        # We do NOT create Territory here; _get_any_territory handles that separately
        if doctype == "Territory":
            return self._get_any_territory()

        existing = frappe.get_all(doctype, pluck="name", limit=1)
        if existing:
            return existing[0]

        # Fallback: create a simple stub for other doctypes
        doc = frappe.get_doc({
            "doctype": doctype,
            doctype.lower(): f"Test {doctype}",
        })
        doc.insert()
        return doc.name

    def _get_default_company(self):
        """Return the default Company, or the first one, or create a minimal stub."""
        company = frappe.db.get_single_value("Global Defaults", "default_company")
        if company:
            return company

        companies = frappe.get_all("Company", pluck="name", limit=1)
        if companies:
            return companies[0]

        # As a last resort, create one
        doc = frappe.get_doc({
            "doctype": "Company",
            "company_name": "Test Company",
            "abbr": "TC",
            "default_currency": "IRR",
        })
        doc.insert()
        return doc.name

    def _get_any_territory(self):
        """Pick an existing Territory; do NOT create a new one."""
        terrs = frappe.get_all("Territory", pluck="name", limit=1)
        # If this blows up, you know your test fixture/site is missing Territories
        self.assertTrue(terrs, "This test requires at least one Territory in the DB")
        return terrs[0]

    def _make_ops_manager_user(self):
        """Create (or fetch) a system user with Ops Manager role."""
        email = "ops.manager@example.com"

        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": "Ops",
            "last_name": "Manager",
            "enabled": 1,
            "user_type": "System User",
            "send_welcome_email": 0,
            "roles": [
                {
                    # Make sure this matches the Role name you ensured via patch/fixtures
                    "role": "Ops Manager",
                },
            ],
        })
        user.insert(ignore_permissions=True)
        return user
    
    def _generate_unique_email(self) -> str:
        """
        Generate a unique email that:
        - looks valid
        - is not used by any existing Employee.personal_email
        """
        while True:
            local_part = f"test.employee.{random.randint(1000, 9999)}"
            email = f"{local_part}@example.com"
            if not frappe.db.exists("Employee", {"personal_email": email}):
                return email
