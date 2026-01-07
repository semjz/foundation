import frappe
from frappe.tests.utils import FrappeTestCase


class TestUserMobileUsername(FrappeTestCase):
    
    def _make_user(self, mobile_no: str, password: str = "TestPassword123"):
        """Helper to create a test user with a given mobile_no."""
        email = f"mobile.test.{frappe.generate_hash(length=6)}@example.com"

        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": "Mobile Test",
            "user_type": "System User",
            "mobile_no": mobile_no,
            "send_welcome_email": 0,
            "new_password": password,
        })

        user.insert(ignore_permissions=True)
        return user

    def test_username_set_on_insert(self):
        """On insert, username should be set from mobile_no (cleaned)."""
        mobile = "0912 333 4444"
        user = self._make_user(mobile)

        # Reload from DB to be extra sure
        user = frappe.get_doc("User", user.name)

        self.assertEqual(user.mobile_no, "09123334444")
        self.assertEqual(user.username, "09123334444")

    def test_username_updates_when_mobile_changes(self):
        """On update, changing mobile_no should update username too."""
        user = self._make_user("09120000000")
        user = frappe.get_doc("User", user.name)

        # Change mobile_no
        user.mobile_no = "0935 111 2222"
        user.save(ignore_permissions=True)

        user = frappe.get_doc("User", user.name)
        self.assertEqual(user.mobile_no, "09351112222")
        self.assertEqual(user.username, "09351112222")

    def test_no_mobile_does_not_touch_username(self):
        """If mobile_no is empty, hook should leave username as-is."""
        # Create a user without mobile_no
        email = f"nomobile.test.{frappe.generate_hash(length=6)}@example.com"
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": "No Mobile",
            "user_type": "System User",
            "send_welcome_email": 0,
            "new_password": "TestPassword123",
        })
        user.insert(ignore_permissions=True)

        # Manually set username
        user.username = "custom_username"
        user.save(ignore_permissions=True)

        # Save again with mobile_no still empty
        user = frappe.get_doc("User", user.name)
        user.save(ignore_permissions=True)

        user = frappe.get_doc("User", user.name)
        self.assertEqual(user.mobile_no, None)
        self.assertEqual(user.username, "custom_username")
