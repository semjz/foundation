# foundation/tests/test_customer_portal_scope.py
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch
import frappe

class TestCustomerPortalScope(FrappeTestCase):
    def setUp(self):
        frappe.flags.in_test = True
        frappe.flags.mute_emails = True

    def _make_customer(self, name, email):
        doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": name,
            "customer_type": "Company",
            "territory": "All Territories",   # swap to a real leaf if you enforce leaf-only
            "primary_email": email,           # align with your hook’s email field
        })
        doc.flags.ignore_mandatory = True
        doc.flags.ignore_tier_mandatory = True
        doc.insert(ignore_permissions=True)
        return doc

    def test_portal_user_is_scoped_to_own_customer(self):
        # suppress welcome email flow triggered by User.insert()
        with patch("frappe.core.doctype.user.user.User.send_welcome_mail_to_user", lambda *a, **k: None):
            cust_a = self._make_customer("Acme A", "acme-a@example.com")
            cust_b = self._make_customer("Acme B", "acme-b@example.com")

        # Users created by the Customer hook
        user_a = frappe.db.get_value("User", {"email": "acme-a@example.com"}, "name")
        user_b = frappe.db.get_value("User", {"email": "acme-b@example.com"}, "name")
        self.assertIsNotNone(user_a)
        self.assertIsNotNone(user_b)

        # User Permissions created by the Customer hook
        self.assertTrue(frappe.db.exists("User Permission", {
            "user": user_a, "allow": "Customer", "for_value": cust_a.name
        }))
        self.assertTrue(frappe.db.exists("User Permission", {
            "user": user_b, "allow": "Customer", "for_value": cust_b.name
        }))

        # User A can read A, not B
        frappe.set_user(user_a)
        self.assertTrue(frappe.has_permission("Customer", doc=cust_a, ptype="read"))
        self.assertFalse(frappe.has_permission("Customer", doc=cust_b, ptype="read"))

        # User B can read B, not A
        frappe.set_user(user_b)
        self.assertTrue(frappe.has_permission("Customer", doc=cust_b, ptype="read"))
        self.assertFalse(frappe.has_permission("Customer", doc=cust_a, ptype="read"))

        frappe.set_user("Administrator")
